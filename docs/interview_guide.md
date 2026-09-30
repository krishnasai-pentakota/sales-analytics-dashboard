# Interview guide

Answers are grounded in what is in this repository. Where something was not done, the answer says so.

## 60 seconds
> I was the only analyst/engineer at a ribbon-and-bow manufacturer where orders, dispatches and the accounts report sat in separate Excel files nobody had reconciled. I built an order-to-cash model with explicit rules — customer versus internal orders, charges billed once per order, a financial year from April — and a five-tab dashboard: sales against last year on a like-for-like basis, customers, product mix, the open order book and on-time delivery. I re-implemented the KPI logic in Python and wrote tests that check it against the dashboard's JavaScript engine, and I reconciled the dashboard to the accounts report: it covers 80 % of value, which I state on the dashboard rather than hide. The data is anonymised real data. The headline finding: year-to-date sales are up 21 %, but one customer drives about 40 % of sales and explains both the June spike and September's dip.

## 2 minutes
Add to the above: *why* it was built that way. The hard part was not charts; it was deciding what a number means. Stock transfers to head office are not sales. DTM and screen charges belong to an order, not a line, so they are allocated once. A half-finished month must be compared with the same days last year. Status uses a 5 % tolerance. I wrote these rules down in a metric dictionary taken from the code, then checked two independent implementations agree to ₹0.01 across seven filter cases. Validation found real issues — 579 order lines with no value, a committed date on only 47 % of lines, 46 committed dates before the PO date — and I surfaced them on the Data tab and in the insights instead of filtering them away. From 1 October a single entry workbook becomes the source, which closes most of these gaps.

## Questions and grounded answers

**What business problem did it solve?** One trusted view of orders, sales, open book and delivery, where previously three files disagreed. See `docs/business_context.md`.

**Who is the user?** Management (Overview), a sales manager (Customers), operations (Orders & delivery), the data owner (Data).

**How did you define net sales?** Invoiced goods value (quantity × rate × unit factor × FX × (1 − discount)) plus once-per-order charges, customer orders only, excluding GST and freight. `docs/metric_dictionary.md`.

**How do you know the numbers are right?** Three layers: 32 tests (including Python-vs-JavaScript parity), a validation report with identities (customer totals sum to the grand total, net = goods + charges), and a reconciliation to the accounts report. The reconciliation shows 80 % coverage, so I say the totals are a floor.

**Why is coverage only 80 %?** The history was rebuilt from dispatch reports, and invoices on 2024 orders are not in them. I did not patch it with estimates. From 1 Oct 2026 the entry workbook is the single source.

**What was the most interesting insight?** June 2026 (+88.5 %) was printed ribbon (₹45.8 L vs ₹2.6 L a year earlier) and one customer at 38.5 %. The accounts report's printing line independently shows ₹45.9 L. So it was a one-off, not a trend.

**What would you recommend to the business?** Treat the top five accounts (88 % of sales) as named accounts; make the committed date mandatory; assign owners to unassigned accounts; short-close open lines older than 90 days.

**What data-quality problems did you find?** See `docs/validation_report.md`: 2.9 % of customer lines unvalued, 53 % without a committed date, 53 identical order lines, 91 invoice lines without a date, 46 committed dates before the PO date.

**What assumptions did you make?** USD at ₹88 (placeholder), 5 % completion tolerance, largest line discount applies to the order, unvalued lines carry no value. `docs/methodology.md`.

**What would you do differently?** Reconcile to the accounts report first, before building views, so coverage is known up front; and capture committed date and rate at order entry from the start — the history lacks them, which is why the 1 Oct workbook does.

**Why HTML/JavaScript rather than Power BI or Tableau?** It is a single self-contained file that needs no server and can load the monthly entry workbook directly in the browser. The trade-off: no governed semantic layer or scheduled refresh. That's why the KPI logic is documented and re-implemented in Python.

**Why Python if the dashboard is JavaScript?** To test the dashboard independently and to generate the insights from code. It is a reference implementation, not a second product.

**What about marketing analytics?** This project has none: there is no spend, lead or channel data. It is sales (order-to-cash) analytics. The same method — define metrics, validate, reconcile — would apply.

**How would it work in production?** See the AI / production section of the README. Those items are a proposal, not built.

**How would you add AI?** Only on top of trusted metrics: forecasting monthly sales, anomaly alerts on customer drop-off (e.g. a top-five customer falling > 50 %), and a natural-language question layer that queries the metric layer rather than the raw tables. None of this is implemented.

**What are the limitations?** No cost or margin; history 80 % of accounts-report value; committed date on 47 % of lines; no credit notes in the data so that logic is tested by rule only; USD rate is a placeholder; 14 % of order lines carry no negotiated rate and fall back to the price list (or stay unvalued).

**What did you personally build?** All of it: extraction and cleaning, the dashboard, the Python reference, tests, validation, documentation. Customer, staff and company names are aliased for publication.
