# Data

`data/processed/` holds the dataset the dashboard is built from. It is the real order-to-cash history of a B2B ribbon and bow manufacturer, **anonymised**:

- the company and its group entities are not named;
- customers appear as `Customer 001 … 041` (units as `Unit A`, `Unit B`), sales staff as `Sales person 1 … 4`;
- dates, quantities, rates, item codes and order / invoice numbers are as recorded (invoice numbers are sequential placeholders).

| File | Rows | What it is |
|---|---:|---|
| `orders.csv` | 20,241 | One row per order line (PO date, account, item, quantity, rate, committed date, charges) |
| `invoice_lines.csv` | 22,615 | One row per invoiced line (document type, date, order link, quantity) |
| `customer_accounts.csv` | 41 | Account → customer, unit, sales person, currency |
| `items.csv` | 7,347 | Item master: ribbon / bow, product type, price-list rate and unit |
| `accounts_reference.csv` | 16 | Monthly sales from the accounts report, used only to reconcile |
| `settings.json` | – | Go-live date, completion tolerance, USD rate placeholder, "today" |

Column-level detail is in [`docs/data_dictionary.md`](../docs/data_dictionary.md).

## What is not here

- The original source workbooks (dispatch reports, the order-entry workbook, the clean masters). They are private and git-ignored.
- The script that turns the private sources into these CSVs. It contains the real-name mapping, so it is not published.

Everything downstream of `data/processed/` — the dashboard build, the KPI reference code, the validation and the tests — is in this repository and reproducible.

## Known gaps in the history

See [`docs/validation_report.md`](../docs/validation_report.md). In short: rate / committed date / supply source are sparsely recorded before 1 Oct 2026; the history covers about 80 % of the accounts-report value for Jan–Aug 2026.
