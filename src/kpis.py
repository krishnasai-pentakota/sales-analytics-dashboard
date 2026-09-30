"""Python reference implementation of the dashboard's KPI logic.

The dashboard (dashboard/template.html) calculates everything in JavaScript. This module
re-implements the same rules in pandas so that:

  * every KPI can be recomputed and audited outside the browser,
  * the tests can check the JavaScript engine against an independent implementation,
  * the business insights in docs/ are generated from code, not typed by hand.

The rules mirror the entry workbook's formulas (see docs/metric_dictionary.md).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

# Rate unit -> multiplier that turns "qty x rate" into rupees.
UNIT_FACTOR = {"PER YARD": 1.0, "PER METRE": 0.9144, "PER ROLL (25 YD)": 1 / 25, "PER PIECE": 1.0, "PER DOZEN": 1 / 12}
DEAD_STATUSES = {"CANCELLED", "DOUBLE ENTRY"}


def _round2(x: float | None) -> float | None:
    """Round half up to 2 decimals, like JavaScript's Math.round (pandas/numpy round half to even)."""
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else float(np.floor(x * 100 + 0.5) / 100)


def derive_item(code: str | None) -> dict:
    """Fallback when an item is missing from the item master: infer from the code pattern.

    Ribbon codes start with five digits (quality series) — first digit 2 = plain, 3/4/6 = printed, 5 = packed roll.
    Anything else is treated as a bow.
    """
    import re
    if not code:
        return {"item_type": None, "product_type": None, "price_list_rate": None, "rate_unit": None}
    c = code.upper()
    if re.match(r"^J?\d{5}-", c):
        d = c.lstrip("J")[0]
        pt = "PLAIN RIBBON" if d == "2" else "PRINTED RIBBON" if d in "346" else "PACKED ROLL" if d == "5" else "TO CONFIRM"
        return {"item_type": "RIBBON", "product_type": pt, "price_list_rate": None, "rate_unit": "PER YARD"}
    return {"item_type": "BOW", "product_type": "TO CONFIRM", "price_list_rate": None, "rate_unit": "PER PIECE"}


@dataclass
class Model:
    orders: pd.DataFrame
    sales: pd.DataFrame
    settings: dict
    data_end: pd.Timestamp
    today: pd.Timestamp


def load_processed() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    orders = pd.read_csv(PROC / "orders.csv", parse_dates=["po_date", "customer_requested_date", "committed_date"])
    sales = pd.read_csv(PROC / "invoice_lines.csv", parse_dates=["invoice_date"])
    accounts = pd.read_csv(PROC / "customer_accounts.csv")
    items = pd.read_csv(PROC / "items.csv")
    settings = json.loads((PROC / "settings.json").read_text())["settings"]
    return orders, sales, accounts, items, settings


def build_model() -> Model:
    orders, sales, accounts, items, S = load_processed()
    golive, tol, usd = pd.Timestamp(S["golive"]), S["tol"], S["usdinr"]

    # --- orders: attach customer and item attributes -------------------------------------------
    acc = accounts.rename(columns={"customer": "cust", "sales_person": "sp", "currency": "cur_acct"}).set_index("account")
    o = orders.join(acc[["customer_id", "cust", "unit", "sp", "cur_acct"]], on="account")
    o["customer_id"] = o.customer_id.where(o.customer_id.notna(), np.where(o.account.notna(), "UNLISTED", None))
    o["sp"] = o.sp.fillna("Unassigned")
    o["currency"] = np.where((o.cur_acct == "USD") & (o.po_date >= golive), "USD", "INR")
    o["fx"] = np.where(o.currency == "USD", usd, 1.0)
    itm = items.set_index("item_code")
    o["item_code"] = o.item_code.str.upper()
    attrs = o.item_code.map(lambda c: itm.loc[c].to_dict() if c in itm.index else derive_item(c))
    a = pd.DataFrame(list(attrs), index=o.index)
    o = pd.concat([o, a[["item_type", "product_type", "price_list_rate", "rate_unit"]]], axis=1)
    o["factor"] = o.rate_unit.map(UNIT_FACTOR).fillna(1.0)
    o["rate_used"] = o.rate.where(o.rate.notna(), o.price_list_rate)
    # one order-level discount: the largest % typed on any line of the order
    o["order_discount"] = o.groupby("order_no").discount_pct.transform("max").fillna(0.0)
    val = o.qty * o.rate_used * o.factor * o.fx * (1 - o.order_discount)
    o["value"] = val.map(_round2)
    o["charges"] = o.dtm_charges.fillna(0) + o.screen_charges.fillna(0)
    o["line"] = o.groupby(["order_no", "item_code"]).cumcount() + 1
    o["key"] = o.order_no + "|" + o.item_code + "|" + o.line.astype(str)

    # --- invoice lines: match to an order line, value, status roll-up ---------------------------
    s = sales.copy()
    s["item_code"] = s.item_code.str.upper()
    s["line_key"] = s.line_no.fillna(1).round().astype(int).astype(str)
    s["key"] = s.order_no + "|" + s.item_code + "|" + s.line_key
    okey = o.drop_duplicates("key").set_index("key")
    s = s.join(okey[["rate_used", "factor", "currency", "order_discount", "order_type", "customer_id", "cust", "sp", "unit", "item_type", "product_type", "account"]], on="key")
    s["matched"] = s.order_type.notna()
    s["rate"] = s.invoice_rate.where(s.invoice_rate.notna(), s.rate_used)
    fx_used = np.where(s.currency == "USD", s.fx_rate.fillna(usd), 1.0)
    sign = np.where(s.document_type == "CREDIT NOTE", -1, 1)
    s["goods"] = (sign * s.qty * s.rate * s.factor * fx_used * (1 - s.order_discount)).where(s.matched & s.qty.notna() & s.rate.notna()).map(_round2)
    # DTM + screen charges are billed once: on the first tax invoice line of each order
    charge_by_order = o.groupby("order_no").charges.sum()
    ti = s.document_type == "TAX INVOICE"
    first_ti = ti & ~s.loc[ti].duplicated("order_no").reindex(s.index, fill_value=True)
    s["charges"] = np.where(first_ti, s.order_no.map(charge_by_order).fillna(0), 0.0)
    s["net"] = s.goods + s.charges
    s["counts"] = (s.document_type != "STOCK TRANSFER DC") & s.matched & (s.order_type == "CUSTOMER")

    # dispatched quantity and last dispatch date per order line (credit notes excluded)
    ship = s[(s.document_type != "CREDIT NOTE") & s.matched & s.qty.notna()].groupby("key").agg(dq=("qty", "sum"), last=("invoice_date", "max"))
    o = o.join(ship, on="key")
    o["dq"] = o.dq.fillna(0.0)
    o["balance"] = o.qty - o.dq
    shipped_enough = o.dq >= o.qty * (1 - tol)
    o["status"] = np.where(o.status_override.notna(), o.status_override, np.where(o.dq == 0, "OPEN", np.where(shipped_enough, "COMPLETED", "PARTIAL")))

    data_end = max(o.po_date.max(), s.invoice_date.max())
    today = max(pd.Timestamp(S["today"]), data_end)
    return Model(o, s, S, data_end, today)


# ------------------------------------------------------------------------------------------------
#  KPI functions. Every one takes a Model and a (start, end) window, and customer-order scope by default.
# ------------------------------------------------------------------------------------------------
def _scope(m: Model, customer_orders_only: bool = True, cat: str = "ALL", customer_id: str = "ALL"):
    o, s = m.orders, m.sales
    mo = pd.Series(True, index=o.index)
    ms = pd.Series(True, index=s.index)
    if customer_orders_only:
        mo &= o.order_type == "CUSTOMER"
        ms &= s.counts
    if cat != "ALL":
        mo &= o.item_type == cat
        ms &= s.item_type == cat
    if customer_id != "ALL":
        mo &= o.customer_id == customer_id
        ms &= s.customer_id == customer_id
    return o[mo], s[ms & s.matched]


def net_sales(m: Model, start, end, **scope) -> float:
    _, s = _scope(m, **scope)
    w = s[(s.invoice_date >= start) & (s.invoice_date <= end) & s.net.notna()]
    return float(w.net.sum())


def orders_received(m: Model, start, end, **scope) -> float:
    o, _ = _scope(m, **scope)
    w = o[(o.po_date >= start) & (o.po_date <= end) & ~o.status.isin(DEAD_STATUSES) & o.value.notna()]
    return float(w.value.sum())


def book_to_bill(m: Model, start, end, **scope) -> float | None:
    ns = net_sales(m, start, end, **scope)
    return orders_received(m, start, end, **scope) / ns if ns else None


def on_time_delivery(m: Model, start, end, **scope) -> tuple[float | None, int]:
    """Share of order lines completed in the window that shipped on or before the committed date."""
    o, _ = _scope(m, **scope)
    w = o[(o.status == "COMPLETED") & o["last"].notna() & o.committed_date.notna() & (o["last"] >= start) & (o["last"] <= end)]
    return (float((w["last"] <= w.committed_date).mean()) if len(w) else None), len(w)


def open_order_book(m: Model, **scope) -> dict:
    """Value still to ship on open/partial lines, and how much of it is past the promised date."""
    o, _ = _scope(m, **scope)
    op = o[o.status.isin(["OPEN", "PARTIAL"])].copy()
    op["bv"] = np.where(op.value.notna() & (op.qty > 0), op.value * op.balance.clip(lower=0) / op.qty, np.nan)
    overdue = op[op.committed_date.notna() & (op.committed_date < m.today)]
    return {"open_value": float(op.bv.sum()), "open_lines": int(len(op)), "overdue_value": float(overdue.bv.sum()), "overdue_lines": int(len(overdue))}


def month_window(year: int, month: int) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(year, month, 1)
    return start, start + pd.offsets.MonthEnd(0)
