"""Assemble dashboard/index.html from the processed CSVs.

    python src/build_dashboard.py

The dashboard is a single self-contained HTML page. Its data is embedded as one JSON
block (dictionary-coded to keep the file small) between the markers in
dashboard/template.html, so the page works by opening it in a browser — no server.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"


def clean(v):
    """NaN -> None, whole floats -> int, so the JSON stays compact and valid."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return int(v) if float(v).is_integer() else float(v)
    return v


def plain(series) -> list:
    return [clean(v) for v in series.tolist()]


def dict_code(series) -> dict:
    """{'d': sorted unique values, 'i': index per row, -1 for missing} — the format the page decodes."""
    values = sorted({v for v in series.dropna().tolist()})
    index = {v: k for k, v in enumerate(values)}
    return {"d": values, "i": [index[v] if isinstance(v, str) else -1 for v in series.tolist()]}


def build_payload() -> dict:
    orders = pd.read_csv(PROC / "orders.csv")
    sales = pd.read_csv(PROC / "invoice_lines.csv")
    accounts = pd.read_csv(PROC / "customer_accounts.csv")
    items = pd.read_csv(PROC / "items.csv")
    ref = pd.read_csv(PROC / "accounts_reference.csv")
    meta = json.loads((PROC / "settings.json").read_text())
    return {
        "version": meta["version"],
        "source": meta["source"],
        "settings": meta["settings"],
        "orders": {
            "po_date": plain(orders.po_date), "account": dict_code(orders.account), "order_no": dict_code(orders.order_no),
            "item": dict_code(orders.item_code), "qty": plain(orders.qty), "rate": plain(orders.rate),
            "order_type": dict_code(orders.order_type), "crd": plain(orders.customer_requested_date),
            "committed": plain(orders.committed_date), "supply": dict_code(orders.supply_source),
            "disc": plain(orders.discount_pct), "dtm": plain(orders.dtm_charges), "screen": plain(orders.screen_charges),
            "override": dict_code(orders.status_override),
        },
        "sales": {
            "doc": dict_code(sales.document_type), "invoice": dict_code(sales.invoice_no), "date": plain(sales.invoice_date),
            "order_no": dict_code(sales.order_no), "item": dict_code(sales.item_code), "qty": plain(sales.qty),
            "line": plain(sales.line_no), "irate": plain(sales.invoice_rate), "gst": plain(sales.gst_pct),
            "freight": plain(sales.freight), "fx": plain(sales.fx_rate),
        },
        "accounts": [[clean(v) for v in row] for row in accounts[["account", "customer_id", "customer", "unit", "customer_type", "sales_person", "currency"]].itertuples(index=False)],
        "items": [[clean(v) for v in row] for row in items[["item_code", "item_type", "product_type", "price_list_rate", "rate_unit"]].itertuples(index=False)],
        "accounts_ref": [[clean(v) for v in row] for row in ref[["month", "bows", "dyeing", "printing"]].itertuples(index=False)],
    }


def main() -> None:
    template = (ROOT / "dashboard" / "template.html").read_text(encoding="utf-8")
    marker = "/*__PAYLOAD__*/"
    assert marker in template, "payload marker missing from template"
    payload = json.dumps(build_payload(), separators=(",", ":"), allow_nan=False)
    html = template.replace(marker, payload.replace("</", "<\\/"))
    out = ROOT / "dashboard" / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  ({len(html)/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
