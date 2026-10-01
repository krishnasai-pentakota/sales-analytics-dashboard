# Dashboard guide

Open `dashboard/index.html` in a browser (it needs internet once for the Plotly and SheetJS CDN scripts). Filters at the top apply to every tab: **Type** (ribbon / bow), **Customer**, **Sales person**, **Orders** (customers only / incl. HQ & stock), **grain** (week … year), **Period**, **Compare** and **Year** basis.

- **Every view is compared two ways:** with the previous period of the same size (previous week, month, quarter or half-year) and with the same period last year. The headline card, the *Answers for this selection* panel and the trend chart (solid line = last year, dashed line = previous period) show both. **Compare** only chooses which one the KPI tiles use. A period still running is compared with the same number of days.
- **Year** (FY Apr–Mar by default, or Jan–Dec) sets how quarters, half-years and years are cut; week and month views are the same either way.

## Overview — "Are we up or down, and why?"
![](../screenshots/executive_overview.png)
- **KPIs:** orders received, dispatched, book-to-bill, open order book (with overdue), on-time delivery, average rate, active customers.
- **Visuals:** year-to-date hero figure vs last year, net sales trend, **seasonality by month of the financial year** (Sales ₹ or Orders ₹, each FY side by side), sales mix, top customers, plain-language answers.
- **Decision:** a period down on last year → check mix and customers before reacting.

## Customers — "Who drives it, and who is slipping?"
![](../screenshots/customer_analysis.png)
- Customer table with change vs comparison, biggest movers, customer × month heatmap, sales-person split.
- **Decision:** a large fall in a top customer (see insight 3) triggers an account conversation; "Unassigned" sales is an ownership gap.

## Products — "What are we selling, at what rate?"
![](../screenshots/product_mix.png)
- Sub-categories, ribbon widths, bow styles, average ribbon and bow rate. Select Ribbons or Bows to populate width/style.
- **Decision:** a rate change alongside a mix change is not a price change.

## Orders & delivery — "What is open, what is late?"
![](../screenshots/orders_and_delivery.png)
- Open order book by age, on-time delivery trend, supply-source mix, largest overdue lines.
- **Decision:** chase the largest overdue lines; ask why committed dates are missing.

## Data — "Can I trust it?"
![](../screenshots/data_quality_and_reconciliation.png)
- What is loaded, reconciliation to the accounts report, how each number is worked out, and loading of the entry workbook / CSVs (loaded rows replace rows with the same order number).

## Rebuild / regenerate
`python src/build_dashboard.py` rebuilds `dashboard/index.html`; `python src/make_screenshots.py …` re-captures the screenshots.
