# Data dictionary

Generated from the actual files in `data/processed/` (row counts and null rates measured, not assumed). Null rates matter: several fields are only filled from 1 Oct 2026, when the order-entry workbook becomes the single source.

## orders.csv — one row per order line (20,241)

| Column | Type | Null | Meaning |
|---|---|---:|---|
| `po_date` | date | 0 % | Date the customer order was received. Drives order intake. |
| `account` | text | 0 % | Ordering account (customer + unit). Joins to `customer_accounts.account`. |
| `order_no` | text | 0 % | Order number (2,897 distinct). |
| `item_code` | text | 0 % | Ordered item. Joins to `items.item_code`. |
| `qty` | number | ~0 % (1 row) | Ordered quantity, in the item's unit (yards for ribbon, pieces for bows). |
| `rate` | number | 14.2 % | Negotiated rate. If empty, the item master's price-list rate is used. |
| `order_type` | text | 0 % | `CUSTOMER` (19,852), `HQ STOCK TRANSFER` (331), `INVENTORY STOCK ORDER` (58). Only `CUSTOMER` counts as sales. |
| `customer_requested_date` | date | 100 % | Not recorded in history; captured from 1 Oct 2026. |
| `committed_date` | date | 53.0 % | Date promised to the customer. On-time delivery can only be measured where present. |
| `supply_source` | text | 50.3 % | Where the goods come from (warehouse stock, HQ import, local dyeing/printing …). 8 values. |
| `discount_pct` | fraction | 100 % | Order-level discount (two values in history: 2 %, 5 %). |
| `dtm_charges` | ₹ | 99.6 % | Digital-print set-up charge; billed once per order. |
| `screen_charges` | ₹ | 99.9 % | Screen charge; billed once per order. |
| `status_override` | text | 95.5 % | Manual status: `CANCELLED` 356, `CLOSED - OLD DATA` 312, `SHORT-CLOSED` 225, `ON HOLD` 7, `DOUBLE ENTRY` 2. Otherwise status is derived. |

## invoice_lines.csv — one row per invoiced line (22,615)

| Column | Type | Null | Meaning |
|---|---|---:|---|
| `document_type` | text | 0 % | `TAX INVOICE` (22,614) or `STOCK TRANSFER DC` (1). `CREDIT NOTE` is supported by the logic but absent from this dataset. |
| `invoice_no` | text | ~0 % | Invoice number (sequential placeholder after anonymisation). |
| `invoice_date` | date | 0.4 % | Dispatch / invoice date. Lines without a date fall in no period. |
| `order_no`, `item_code` | text | 0 % | Link to the order line. Every invoice line matches an order line. |
| `qty` | integer | 0 % | Invoiced quantity. |
| `line_no` | integer | 98.3 % | Distinguishes repeated items on one order. Empty = first occurrence. |
| `invoice_rate`, `freight`, `fx_rate` | number | 100 % | Not in history; populated from the 1 Oct 2026 entry file. |
| `gst_pct` | % | 31.6 % | GST rate (0 / 5 / 12 / 18). Informational; not used in net sales. |

## customer_accounts.csv — one row per account (41)

| Column | Meaning |
|---|---|
| `account` | Account name (`Customer 001 Unit A`). Primary key. |
| `customer_id`, `customer` | Parent customer (40 IDs). Several customers have more than one account/unit. |
| `unit` | `Unit A`, `Unit B` or `MAIN`. |
| `customer_type` | `Customer` (39) or `Internal` (HQ stock transfer, stock order). |
| `sales_person` | Owning sales person; **56 % of accounts have none assigned** (shown as "Unassigned"). |
| `currency` | `INR` (40) or `USD` (1). USD converts at the placeholder rate from go-live. |

## items.csv — item master (7,347)

| Column | Meaning |
|---|---|
| `item_code` | Primary key. |
| `item_type` | `RIBBON` or `BOW`. |
| `product_type` | `PLAIN RIBBON`, `PRINTED RIBBON`, `PACKED ROLL`, `HAND MADE BOW`, `MACHINE MADE BOW`, `TO CONFIRM`. |
| `price_list_rate` | Price-list rate (22.4 % missing). |
| `rate_unit` | `PER YARD` / `PER PIECE` in this file; the logic also supports metre, roll, dozen. |

## accounts_reference.csv — 16 months

Monthly sales from the accounts report, split `bows`, `dyeing`, `printing` (₹). Used only to reconcile the dashboard; never enters a KPI.

## settings.json

`golive` 2026-10-01 · `tol` 0.05 (a line is complete when ≥ 95 % shipped) · `usdinr` 88 (**placeholder**) · `today` 2026-09-30.

## Relationships

```
customer_accounts 1 ─── * orders 1 ─── * invoice_lines
                              * ─── 1 items
```
Invoice line → order line on `order_no + item_code + line_no`.
