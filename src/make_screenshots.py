"""Capture README screenshots of the dashboard with headless Chromium.

    python src/make_screenshots.py --plotly path/to/plotly.min.js

The dashboard loads Plotly and SheetJS from public CDNs. On a machine without internet
access pass --plotly (any plotly.js 2.x/3.x bundle) and the capture serves it locally;
on a normal machine omit it and the CDN is used.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SHOTS = [("overview", "executive_overview.png"), ("customers", "customer_analysis.png"), ("products", "product_mix.png"),
         ("delivery", "orders_and_delivery.png"), ("data", "data_quality_and_reconciliation.png")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plotly", help="local plotly.min.js to serve instead of the CDN")
    ap.add_argument("--chromium", help="path to a Chromium executable (optional)")
    args = ap.parse_args()
    out = ROOT / "screenshots"
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium, args=["--no-sandbox"]) if args.chromium else p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        if args.plotly:
            js = Path(args.plotly).read_text(encoding="utf-8")
            page.route("**/plotly*.js", lambda r: r.fulfill(body=js, content_type="application/javascript"))
            page.route("**/xlsx*.js", lambda r: r.fulfill(body="window.XLSX=window.XLSX||{};", content_type="application/javascript"))
        page.goto((ROOT / "dashboard" / "index.html").as_uri(), wait_until="load")
        page.wait_for_selector(".js-plotly-plot", timeout=30000)
        page.wait_for_timeout(2500)
        for tab, name in SHOTS:
            page.click(f"#tab-{tab}")
            if tab == "products":                       # with "All" selected this tab shows an empty prompt; Ribbons shows the trend charts
                page.click('#f-cat button[data-v="RIBBON"]')
            page.wait_for_timeout(2500)
            page.screenshot(path=str(out / name), full_page=True)
            if tab == "products":
                page.click('#f-cat button[data-v="ALL"]')
            print("saved", name)
        browser.close()


if __name__ == "__main__":
    main()
