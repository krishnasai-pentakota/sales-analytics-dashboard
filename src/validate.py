"""Data-quality checks on the processed data. Writes docs/validation_report.md.

    python src/validate.py

Every number in the report is computed here, from data/processed/, so the report can be regenerated.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src import kpis

ROOT = Path(__file__).resolve().parents[1]
VALID_ORDER_TYPES = {"CUSTOMER", "HQ STOCK TRANSFER", "INVENTORY STOCK ORDER"}
VALID_DOC_TYPES = {"TAX INVOICE", "STOCK TRANSFER DC", "CREDIT NOTE"}
VALID_OVERRIDES = {"CANCELLED", "CLOSED - OLD DATA", "DOUBLE ENTRY", "ON HOLD", "SHORT-CLOSED"}


def main() -> str:
    m = kpis.build_model()
    o, s = m.orders, m.sales
    orders, sales, accounts, items, _ = kpis.load_processed()
    rows: list[tuple[str, str, str, str]] = []   # (area, check, result, note)

    def add(area, check, value, note="", bad=False):
        rows.append((area, check, f"{'⚠ ' if bad else '✓ '}{value}", note))

    # --- completeness ---------------------------------------------------------------------------
    add("Completeness", "Order lines / invoice lines / accounts / items", f"{len(orders):,} / {len(sales):,} / {len(accounts)} / {len(items):,}")
    for col in ["po_date", "account", "order_no", "item_code", "qty"]:
        n = int(orders[col].isna().sum()); add("Completeness", f"orders.{col} missing", f"{n:,}", bad=n > 0)
    n = int(orders.committed_date.isna().sum()); add("Completeness", "orders with no committed date", f"{n:,} ({n/len(orders):.1%})", "on-time delivery can only be measured where a date exists", bad=n > 0)
    n = int(((o.value.isna()) & (o.order_type == "CUSTOMER")).sum()); add("Completeness", "customer order lines that cannot be valued (no rate and no price-list rate, or no quantity)", f"{n:,} ({n/(o.order_type=='CUSTOMER').sum():.1%})", "matches the dashboard's Data tab; these lines carry no value in any total", bad=n > 0)
    n = int(sales.invoice_date.isna().sum()); add("Completeness", "invoice lines with no date", f"{n:,}", "such lines are in no period", bad=n > 0)
    n = int((sales.invoice_no == "NOT RECORDED").sum()); add("Completeness", "invoice lines with no invoice number", f"{n:,}", bad=n > 0)

    # --- validity -------------------------------------------------------------------------------
    lo, hi = pd.Timestamp("2024-01-01"), m.data_end
    bad_po = int(((orders.po_date < lo) | (orders.po_date > hi)).sum()); add("Validity", f"PO dates outside {lo.date()} … {hi.date()}", f"{bad_po}", bad=bad_po > 0)
    bad_inv = int(((sales.invoice_date < lo) | (sales.invoice_date > hi)).sum()); add("Validity", "invoice dates outside the same range", f"{bad_inv}", bad=bad_inv > 0)
    n = int((orders.committed_date < orders.po_date).sum()); add("Validity", "committed date earlier than PO date", f"{n}", bad=n > 0)
    n = int((orders.qty <= 0).sum()); add("Validity", "orders with zero or negative quantity", f"{n}", bad=n > 0)
    n = int((orders.rate < 0).sum()); add("Validity", "orders with negative rate", f"{n}", bad=n > 0)
    n = int((sales.qty < 0).sum()); add("Validity", "invoice lines with negative quantity", f"{n}", "credit notes are signed by document type, not by quantity", bad=n > 0)
    bad_ot = set(orders.order_type.dropna()) - VALID_ORDER_TYPES; add("Validity", "order types outside the agreed list", str(sorted(bad_ot)) if bad_ot else "none", bad=bool(bad_ot))
    bad_doc = set(sales.document_type.dropna()) - VALID_DOC_TYPES; add("Validity", "document types outside the agreed list", str(sorted(bad_doc)) if bad_doc else "none", bad=bool(bad_doc))
    bad_ov = set(orders.status_override.dropna()) - VALID_OVERRIDES; add("Validity", "status overrides outside the agreed list", str(sorted(bad_ov)) if bad_ov else "none", bad=bool(bad_ov))
    odd_gst = sales.gst_pct.dropna(); odd_gst = odd_gst[~odd_gst.isin([0, 0.05, 0.12, 0.18, 5, 12, 18])]; add("Validity", "GST % other than 0 / 5 / 12 / 18", f"{len(odd_gst)}", bad=len(odd_gst) > 0)

    # --- uniqueness / referential integrity -------------------------------------------------------
    n = int(o.duplicated(["order_no", "item_code", "line"]).sum()); add("Uniqueness", "duplicate order-line keys (order + item + occurrence)", f"{n}", "occurrence number makes repeats of the same item on one order distinct by design", bad=n > 0)
    n = int(orders.duplicated().sum()); add("Uniqueness", "order lines identical in every field", f"{n:,}", "possible double entry — kept, because the same line can legitimately repeat", bad=n > 0)
    n = int(sales.duplicated().sum()); add("Uniqueness", "invoice lines identical in every field", f"{n:,}", bad=n > 0)
    unk = set(orders.account.dropna()) - set(accounts.account); add("Integrity", "order accounts missing from the customer master", str(len(unk)), bad=bool(unk))
    unk_items = set(orders.item_code.dropna().str.upper()) - set(items.item_code); add("Integrity", "ordered item codes missing from the item master", f"{len(unk_items):,}", "product type is then inferred from the code", bad=bool(unk_items))
    um = s[~s.matched]; add("Integrity", "invoice lines that match no order line", f"{len(um):,} ({len(um)/len(s):.1%})", "every invoice line links to an order line" if len(um) == 0 else "invoices on orders missing from the order history", bad=len(um) > 0)
    add("Integrity", "orders flagged cancelled / double entry (excluded from order intake)", f"{int(o.status.isin(kpis.DEAD_STATUSES).sum()):,}")

    # --- calculation consistency ------------------------------------------------------------------
    cs = s[s.counts & s.net.notna()]
    add("Calculation", "net = goods + charges on every counted invoice line", "holds" if np.allclose(cs.net, cs.goods + cs.charges) else "fails", bad=not np.allclose(cs.net, cs.goods + cs.charges))
    by_cust = cs.groupby("customer_id").net.sum().sum()
    add("Calculation", "customer totals add up to the grand total", f"{by_cust:,.2f} = {cs.net.sum():,.2f}", bad=not np.isclose(by_cust, cs.net.sum()))
    cn = s[(s.document_type == "CREDIT NOTE") & s.goods.notna()]
    add("Calculation", "credit notes reduce sales (goods ≤ 0)", (f"{len(cn)} credit-note lines, all ≤ 0" if len(cn) else "no credit notes in this dataset") if (cn.goods <= 0).all() else "fails", bad=not (cn.goods <= 0).all())
    add("Calculation", "internal HQ / stock documents excluded from customer sales", f"{int((~s.counts & s.matched).sum()):,} lines excluded")

    # --- reconciliation with the accounts report -------------------------------------------------
    ref = pd.read_csv(ROOT / "data" / "processed" / "accounts_reference.csv")
    ref["accounts_total"] = ref[["bows", "dyeing", "printing"]].sum(axis=1)
    monthly = cs.assign(month=cs.invoice_date.dt.strftime("%Y-%m")).groupby("month").net.sum()
    ref["dashboard"] = ref.month.map(monthly).fillna(0.0)
    ref["coverage"] = ref.dashboard / ref.accounts_total
    r26 = ref[ref.month >= "2026-01"]
    add("Reconciliation", "Jan–Aug 2026: dashboard vs accounts report", f"₹{r26.dashboard.sum()/1e7:.2f} Cr vs ₹{r26.accounts_total.sum()/1e7:.2f} Cr ({r26.dashboard.sum()/r26.accounts_total.sum():.0%})", "the history is rebuilt from dispatch reports; older invoices are not in them", bad=True)

    lines = ["# Data validation report", "", "*Generated by `python src/validate.py` from `data/processed/`. A ⚠ marks something to know about, not necessarily an error.*", "",
             "| Area | Check | Result | Note |", "|---|---|---|---|"]
    lines += [f"| {a} | {c} | {r} | {n} |" for a, c, r, n in rows]
    lines += ["", "## Monthly reconciliation — dashboard net sales vs accounts report (₹ lakh)", "", "| Month | Accounts report | Dashboard | Coverage |", "|---|---:|---:|---:|"]
    lines += [f"| {r.month} | {r.accounts_total/1e5:,.1f} | {r.dashboard/1e5:,.1f} | {r.coverage:.0%} |" for r in ref.itertuples()]
    lines += ["", "Months before April 2025 are low because invoices on 2024 orders are not in the source dispatch reports, so comparisons start from April 2025. The accounts report has no entries for September–December 2025 in this dataset."]
    text = "\n".join(lines) + "\n"
    (ROOT / "docs" / "validation_report.md").write_text(text, encoding="utf-8")
    return text


if __name__ == "__main__":
    print(main())
