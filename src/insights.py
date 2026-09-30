"""Compute the headline facts quoted in docs/business_insights.md.

    python -m src.insights

Prints every figure used in the insights document, so each statement can be traced to code.
"""
from __future__ import annotations

import pandas as pd

from src import kpis


def lakh(x): return f"₹{x/1e5:,.1f} L"
def cr(x): return f"₹{x/1e7:,.2f} Cr"


def main() -> None:
    m = kpis.build_model()
    o, s = m.orders, m.sales
    cs = s[s.counts & s.net.notna()].copy()
    cs["month"] = cs.invoice_date.dt.to_period("M")
    print("data end", m.data_end.date(), "| customer invoice lines", len(cs), "| customers invoiced", cs.customer_id.nunique())

    # headline periods
    for label, (a, b), (ya, yb) in [
        ("Sep 2026", kpis.month_window(2026, 9), kpis.month_window(2025, 9)),
        ("Aug 2026", kpis.month_window(2026, 8), kpis.month_window(2025, 8)),
        ("Jun 2026", kpis.month_window(2026, 6), kpis.month_window(2025, 6)),
    ]:
        cur, ly = kpis.net_sales(m, a, b), kpis.net_sales(m, ya, yb)
        print(f"{label}: net {lakh(cur)} vs LY {lakh(ly)} ({cur/ly-1:+.1%}) | orders {lakh(kpis.orders_received(m, a, b))} | b2b {kpis.book_to_bill(m, a, b):.2f} | otd {kpis.on_time_delivery(m, a, b)}")
    fy_a, fy_b = pd.Timestamp(2026, 4, 1), m.data_end
    fy_ly_a, fy_ly_b = pd.Timestamp(2025, 4, 1), m.data_end - pd.DateOffset(years=1)
    cur, ly = kpis.net_sales(m, fy_a, fy_b), kpis.net_sales(m, fy_ly_a, fy_ly_b)
    print(f"FY26-27 to date (Apr 1 – {m.data_end.date()}): {cr(cur)} vs {cr(ly)} same days last year ({cur/ly-1:+.1%})")
    cy_a = pd.Timestamp(2026, 1, 1); cur, ly = kpis.net_sales(m, cy_a, fy_b), kpis.net_sales(m, pd.Timestamp(2025, 1, 1), fy_b - pd.DateOffset(years=1))
    print(f"Calendar YTD: {cr(cur)} vs {cr(ly)} ({cur/ly-1:+.1%})  [Jan–Mar 2025 incomplete — see validation report]")

    # monthly trend
    mt = cs.groupby("month").net.sum()
    print("\nMonthly net sales (₹ L):"); print((mt/1e5).round(1).to_string())

    # concentration — financial year to date and trailing twelve months
    def conc(label, a, b):
        w = cs[(cs.invoice_date >= a) & (cs.invoice_date <= b)]
        t = w.groupby("customer_id").net.sum().sort_values(ascending=False)
        tot = t.sum()
        print(f"\nConcentration {label}: total {cr(tot)}, {len(t)} customers; top1 {t.iloc[0]/tot:.1%} ({t.index[0]}), top3 {t.iloc[:3].sum()/tot:.1%}, top5 {t.iloc[:5].sum()/tot:.1%}, top10 {t.iloc[:10].sum()/tot:.1%}")
        print("  top 6:", [(i, f"{v/tot:.1%}") for i, v in t.iloc[:6].items()])
        return t
    conc("FY26-27 to date", fy_a, fy_b)
    conc("Jan–Aug 2026", pd.Timestamp(2026, 1, 1), pd.Timestamp(2026, 8, 31))
    tw = conc("Sep 2026", *kpis.month_window(2026, 9))

    # unit split of the largest customer in Sep 2026
    w = cs[(cs.invoice_date >= pd.Timestamp(2026, 9, 1)) & (cs.customer_id == "CUS001")]
    print("  CUS001 units Sep 2026:", (w.groupby("unit").net.sum()/1e5).round(1).to_dict())

    # product mix, FY to date
    w = cs[(cs.invoice_date >= fy_a)]
    print("\nFY26-27 to date by item type:", (w.groupby("item_type").net.sum()/w.net.sum()).round(3).to_dict())
    print("by product type:", (w.groupby("product_type").net.sum()/w.net.sum()).round(3).sort_values(ascending=False).to_dict())
    rib = w[(w.item_type == "RIBBON") & w.goods.notna() & (w.document_type != "CREDIT NOTE")]
    print("avg ribbon rate ₹/yd:", round(rib.goods.sum()/rib.qty.sum(), 2), "| yards", f"{rib.qty.sum():,.0f}")
    bow = w[(w.item_type == "BOW") & w.goods.notna() & (w.document_type != "CREDIT NOTE")]
    print("avg bow rate ₹/pc:", round(bow.goods.sum()/bow.qty.sum(), 2), "| pieces", f"{bow.qty.sum():,.0f}")

    # sales person split FY to date
    sp = w.assign(sp=w.sp.fillna("Unassigned")).groupby("sp").net.sum().sort_values(ascending=False)
    print("\nBy sales person (FY to date):", {k: f"{v/sp.sum():.1%}" for k, v in sp.items()})
    wa = cs[(cs.invoice_date >= pd.Timestamp(2026, 1, 1))]
    un = wa[wa.sp == "Unassigned"]; print(f"2026 sales on accounts with no sales person: {cr(un.net.sum())} across {un.customer_id.nunique()} customers ({un.net.sum()/wa.net.sum():.1%})")

    # September product-type movement and realised rates
    sa, sb = kpis.month_window(2026, 9); ya, yb = kpis.month_window(2025, 9)
    cur = cs[(cs.invoice_date >= sa) & (cs.invoice_date <= sb)].groupby("product_type").net.sum(); prv = cs[(cs.invoice_date >= ya) & (cs.invoice_date <= yb)].groupby("product_type").net.sum()
    print("\nSep product types (₹ L) now vs last year:", {k: (round(float(cur.get(k, 0))/1e5, 1), round(float(prv.get(k, 0))/1e5, 1)) for k in sorted(set(cur.index) | set(prv.index))})
    def rate(a, b, cat):
        w = cs[(cs.invoice_date >= a) & (cs.invoice_date <= b) & (cs.item_type == cat) & (cs.document_type != "CREDIT NOTE") & cs.goods.notna()]; return w.goods.sum()/w.qty.sum()
    print("Sep avg ribbon ₹/yd", round(rate(sa, sb, "RIBBON"), 2), "vs LY", round(rate(ya, yb, "RIBBON"), 2), "| bow ₹/pc", round(rate(sa, sb, "BOW"), 2), "vs LY", round(rate(ya, yb, "BOW"), 2))

    pr = cs[cs.product_type == "PRINTED RIBBON"].groupby("month").net.sum()/1e5
    print("Printed ribbon net sales by month (₹ L):", {str(k): round(float(v), 1) for k, v in pr.items() if str(k) >= "2025-04"})

    # the June 2026 spike: what drove it?
    a, b = kpis.month_window(2026, 6); jun = cs[(cs.invoice_date >= a) & (cs.invoice_date <= b)]
    print("\nJun 2026 by product type (₹ L):", (jun.groupby("product_type").net.sum()/1e5).round(1).sort_values(ascending=False).to_dict())
    print("Jun 2026 top customers:", {k: f"{v/jun.net.sum():.1%}" for k, v in jun.groupby("customer_id").net.sum().sort_values(ascending=False).head(4).items()})
    jl = cs[(cs.invoice_date >= pd.Timestamp(2025, 6, 1)) & (cs.invoice_date <= pd.Timestamp(2025, 6, 30))]
    print("Jun 2025 by product type (₹ L):", (jl.groupby("product_type").net.sum()/1e5).round(1).sort_values(ascending=False).to_dict())
    ref = pd.read_csv(kpis.PROC / "accounts_reference.csv"); print("Accounts report Jun 2026 bows/dyeing/printing (₹ L):", (ref[ref.month == "2026-06"][["bows", "dyeing", "printing"]].iloc[0]/1e5).round(1).to_dict())

    # delivery
    print("\nOn-time delivery by month (lines completed, % on time):")
    for mo in pd.period_range("2026-01", "2026-09", freq="M"):
        a, b = kpis.month_window(mo.year, mo.month); otd, n = kpis.on_time_delivery(m, a, b); print(f"  {mo}: {otd:.0%} of {n}" if otd is not None else f"  {mo}: n/a")
    ob = kpis.open_order_book(m); print("Open book:", {k: (lakh(v) if 'value' in k else v) for k, v in ob.items()})
    op = o[(o.order_type == "CUSTOMER") & o.status.isin(["OPEN", "PARTIAL"])].copy()
    op["bv"] = op.value * op.balance.clip(lower=0) / op.qty
    op["age"] = (m.today - op.po_date).dt.days
    bins = pd.cut(op.age, [-1, 15, 30, 60, 90, 10**6], labels=["0–15", "16–30", "31–60", "61–90", "90+"])
    print("Open book ageing (₹ L, lines):", {k: (round(float(v.bv.sum())/1e5, 1), len(v)) for k, v in op.groupby(bins, observed=False)})
    print("committed date present on", f"{o.committed_date.notna().mean():.1%}", "of order lines")

    # orders vs sales
    supply = o[(o.order_type == "CUSTOMER") & (o.po_date >= fy_a) & ~o.status.isin(kpis.DEAD_STATUSES)].groupby(o.supply_source.fillna("Not recorded")).value.sum()
    print("\nFY order intake by supply source:", (supply/supply.sum()).round(3).sort_values(ascending=False).to_dict())
    print("status mix (customer orders, FY):", o[(o.order_type == "CUSTOMER") & (o.po_date >= fy_a)].status.value_counts().to_dict())
    print("Cancelled/double-entry lines:", int(o.status.isin(kpis.DEAD_STATUSES).sum()), "of", len(o))


if __name__ == "__main__":
    main()
