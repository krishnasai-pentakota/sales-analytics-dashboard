# Business insights

Every figure below is computed from `data/processed/` by `python -m src.insights` (raw output in [`insight_facts.txt`](insight_facts.txt)) and agrees with the dashboard. Customers are aliases. ₹ L = lakh (100,000); ₹ Cr = crore (10 million). "Interpretation" is reasoning, not something the data proves; where the data cannot settle a point it says so.

## 1. Year to date is up, but the latest month is down
- **Finding:** Sep 2026 net sales fell 7.1 % on Sep 2025 while the financial year is up 20.7 %.
- **Evidence:** Sep 2026 ₹71.0 L vs ₹76.4 L. FY 2026-27 to 30 Sep ₹4.81 Cr vs ₹3.99 Cr (same days last year). Aug 2026 was +2.1 % (₹70.1 L vs ₹68.7 L). Calendar YTD +40.2 % is **not** reliable: Jan–Mar 2025 is under-covered.
- **Interpretation:** the year's growth is front-loaded by June (insight 2); the run-rate since July is flat to slightly down on last year.
- **Action:** report growth on an FY like-for-like basis from April 2025, and track the monthly run-rate separately from YTD.

## 2. June 2026 was a one-customer, one-product spike
- **Finding:** June 2026 net sales (₹107.3 L, +88.5 % vs ₹57.0 L) were driven by printed ribbon and one customer.
- **Evidence:** printed ribbon ₹45.8 L in June 2026 vs ₹2.6 L in June 2025 and ₹3.2 L in July 2026. Customer 003 was 38.5 % of June sales (₹41.3 L in the month) and has billed ₹0–13 L in every other month since April 2025. The accounts report's printing component for June 2026 is ₹45.9 L, which corroborates it independently.
- **Interpretation:** a large, non-recurring printed-ribbon order, not a change in run-rate. Book-to-bill was 0.49 in June (orders ₹52.6 L), consistent with billing a backlog.
- **Action:** don't use June as a baseline for targets; find out whether the order repeats.

## 3. Sales depend on very few customers
- **Finding:** three customers are 72 % of FY-to-date sales; one is 40 %.
- **Evidence (25 customers invoiced, ₹4.81 Cr):** top 1 39.7 %, top 3 72.0 %, top 5 88.1 %, top 10 98.2 %. In Sep 2026 the top customer was 49.5 % (its two units: ₹16.3 L and ₹18.9 L). Customer 003 fell from ₹13.2 L (Sep 2025) to ₹1.1 L (Sep 2026), −92 %, which alone is more than the whole −₹5.3 L decline of the month.
- **Interpretation:** a change at one or two accounts moves the whole business; the Sep dip is one customer's pause, not broad weakness.
- **Action:** treat the top five as named accounts with a review cadence; ask what Customer 003 has planned; track the long tail for diversification.

## 4. Product mix shifted within September
- **Finding:** hand-made bows and plain ribbon up, printed ribbon and machine-made bows down.
- **Evidence (Sep 2026 vs Sep 2025, ₹ L):** hand-made bows 13.7 vs 5.6; machine-made bows 3.5 vs 5.2; plain ribbon 47.6 vs 44.1; printed ribbon 5.9 vs 20.4. FY to date: ribbon 78.5 %, bows 21.5 % (plain ribbon 58.6 %, printed 19.2 %, hand-made bows 13.0 %, machine-made 8.4 %).
- **Interpretation:** printed ribbon is lumpy (monthly ₹1.4–45.8 L since May 2025) and dominates month-to-month variance. Realised rates move with mix: bows ₹1.14/pc vs ₹0.81 last Sep; ribbon ₹1.89 vs ₹1.84/yd — a mix effect, not a price list change (the data cannot separate the two).
- **Action:** plan printed-ribbon capacity around known orders; compare rates only within a product type.

## 5. Delivery: less than 60 % on time, and the measure covers under half the lines
- **Finding:** on-time delivery is 42–61 % by month in 2026.
- **Evidence:** Sep 2026 57.7 % of 286 completed lines; Jul 61 %; Jun 44 %; Jan 42 %. A committed date exists on only 47 % of order lines.
- **Interpretation:** real delivery performance is probably not better than this (lines with dates are the ones someone tracked), but it is unmeasured for over half of the lines. A missing date cannot be late, so the open-book overdue figure below is also a lower bound.
- **Action:** make the committed date mandatory at order entry (the 1 Oct workbook captures it); set a target and review it monthly.

## 6. Open order book: ₹75.9 L to ship, ₹20.3 L past the promised date
- **Finding:** 645 lines are open or part-shipped, worth ₹75.9 L; 126 lines (₹20.3 L) are past their committed date.
- **Evidence:** ageing (₹ L, lines): 0–15 d 24.7 / 288; 16–30 d 8.4 / 101; 31–60 d 28.6 / 178; 61–90 d 13.1 / 37; 90+ d 1.1 / 41. Sep 2026 book-to-bill 1.09, Aug 1.27.
- **Interpretation:** the bulk is young (0–15 d), but ₹28.6 L sits at 31–60 days and 41 lines are older than 90 days — candidates for short-close or follow-up. Book-to-bill above 1 in Aug–Sep means the book is growing.
- **Action:** review the largest overdue lines weekly; short-close stale lines so the book stays meaningful.

## 7. Ownership gap in sales attribution
- **Finding:** 8.6 % of FY-to-date sales have no sales person.
- **Evidence:** Sales person 1 40.0 %, Sales person 2 33.0 %, Sales person 4 16.5 %, Unassigned 8.6 %, Sales person 3 1.9 %. In 2026, ₹0.61 Cr (8.8 %) was on 13 customers with no owner.
- **Interpretation:** performance by sales person is understated for the assigned ones and unknown for the rest.
- **Action:** assign an owner to each account (open item in the project list).

## 8. Data completeness limits how far the numbers can be pushed
- **Finding:** the history covers about 80 % of accounts-report value and several fields are sparse.
- **Evidence:** Jan–Aug 2026 ₹6.21 Cr vs ₹7.81 Cr (80 %; monthly 69–91 %). 2.9 % of customer order lines have no value. Supply source is not recorded on 72 % of FY order intake. 358 of 20,241 order lines are cancelled or double entries.
- **Interpretation:** totals are a floor, not the accounts-report figure; ratios and rankings are more robust than absolute levels.
- **Action:** use the 1 Oct 2026 entry workbook as the single source and re-run the reconciliation monthly.

## 9. No reliable peak or low season yet
- **Finding:** the data shows no consistent peak or low season; one full financial year is not enough to claim one.
- **Evidence (net sales, ₹ L):** FY25-26 by quarter: Apr–Jun 170.7, Jul–Sep 228.2, Oct–Dec 213.5, Jan–Mar 210.8; highest month Jul (83.1), lowest Apr (54.2). The months that repeat disagree: Apr–Jun 2026 was 280.3 vs 170.7 a year earlier (+64 %), then Jul–Sep 2026 is 201.1 vs 228.2 (−11.9 %). FY-to-date is still +20.7 %.
- **Interpretation:** month-to-month swings here come mainly from a few large orders (insights 2 and 3), not from a calendar pattern. Indian festive and gifting months (roughly Sep–Nov), the wedding season and year-end could plausibly matter for ribbons and bows, but that is general market context, not something this dataset shows.
- **Action:** keep the Seasonality card on the Overview tab; after Mar 2027 the second year will allow a real month-by-month comparison. Meanwhile ask the sales team which customers order ahead of festivals and check their order dates.

## What this data cannot answer
Marketing ROI, lead conversion, margin, customer profitability, price elasticity. The dataset has no spend, lead, cost or channel fields.
