# Metric dictionary

Every definition below is taken from the dashboard's JavaScript engine (`dashboard/template.html`) and re-implemented in `src/kpis.py`. `tests/test_kpis.py` checks the two agree to ₹0.01.

**Scope rule.** Unless stated, figures are *customer orders only*: an invoice line counts when its document is not a stock-transfer DC, it matches an order line, and that order's type is `CUSTOMER`. The *Orders* filter can widen scope to HQ / stock orders.

| KPI | Definition | Notes |
|---|---|---|
| **Line value (goods)** | `sign × qty × rate × unit factor × fx × (1 − order discount)` | `sign` −1 for credit notes. `rate` = invoice rate, else order rate, else price-list rate. Unit factors: yard 1, metre 0.9144, roll (25 yd) 1/25, piece 1, dozen 1/12. Rounded half-up to 2 dp. |
| **Charges** | DTM + screen charges of the order | Billed **once per order**, on its first tax invoice line. |
| **Net sales** | `goods + charges` over counted invoice lines in the period, by invoice date | Excludes GST and freight. USD accounts × `usdinr` from go-live. |
| **Orders received** | Σ order-line value by PO date | Excludes `CANCELLED` and `DOUBLE ENTRY`. Lines that cannot be valued are excluded (2.9 %). |
| **Dispatched** | Σ invoiced quantity — ribbon in yards, bows in pieces | Credit notes excluded from quantity. |
| **Book-to-bill** | Orders received ÷ net sales, same period | > 1 = order book growing; < 1 = billing more than new orders. |
| **Order-line status** | Manual override if present; else `OPEN` (nothing shipped), `COMPLETED` (shipped ≥ 95 % of ordered), else `PARTIAL` | Tolerance `tol = 0.05`. |
| **Open order book** | Σ `value × balance ÷ qty` on `OPEN` and `PARTIAL` lines, as of "today" | Overridden lines (cancelled, short-closed …) are not open. |
| **Past promised date (overdue)** | Open book where `committed_date < today` | Lines with no committed date are open but cannot be overdue. |
| **On-time delivery (OTD)** | Share of lines `COMPLETED` in the period whose last dispatch date ≤ committed date | Only lines with a committed date (47 % of order lines); the count of lines is always shown beside the %. |
| **Average ribbon rate** | Ribbon goods value ÷ yards invoiced (₹/yd) | Realised rate, so it moves with mix. |
| **Average bow rate** | Bow goods value ÷ pieces invoiced (₹/pc) | |
| **Active customers** | Distinct customers invoiced in the period | Units roll up to the parent customer. |
| **Top-customer share** | Customer net sales ÷ total, ranked | Top-N shares in `docs/business_insights.md`. |
| **Product type** | From the item master; if the item is missing, inferred from the code: first digit 2 = plain, 3/4/6 = printed, 5 = packed roll; other codes = bow | In this dataset every ordered item is in the master. |

## Period and comparison conventions

- **Grain:** week, month, quarter, half-year, year. **Year basis:** calendar (Jan–Dec) or financial (Apr–Mar).
- **Compare:** vs the previous period (default) or vs the same period last year; the trend chart follows the choice. For a partial period the comparison covers the **same number of days** (like-for-like), so a half-finished month is never compared with a full one.
- Comparisons are only reliable from **April 2025**: earlier months are under-covered (see the reconciliation in `validation_report.md`).

## Not defined here (no data)

Marketing spend, leads, channel attribution, CAC, ROAS, pipeline stages, win rate. This project has order-to-cash data only.
