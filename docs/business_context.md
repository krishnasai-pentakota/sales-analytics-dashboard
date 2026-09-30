# Business context

## The business
A B2B manufacturer of ribbons (plain, printed, packed rolls) and bows (hand-made, machine-made), selling to a small number of repeat customers. Some customers order through several units or sites. A head-office stock entity also raises internal stock-transfer and inventory orders, which are not sales.

## The problem
Management could not answer, from one place, basic order-to-cash questions:

- How much did we sell this month, and how does it compare with last year on a fair basis?
- Which customers and product types drive that — and how dependent are we on a few?
- How much have customers ordered that we have not yet shipped, and how much of it is late?
- Do we deliver when we promised?

Orders, dispatches and the accounts report lived in separate Excel files that were never reconciled. A financial year that starts in April, a calendar-year report, internal stock transfers mixed in with customer orders, and charges billed once per order (not per line) made the numbers easy to get wrong.

## What this project does
Turns those files into one order-to-cash model with explicit, documented rules, a five-tab dashboard, a reference implementation in Python that is tested against the dashboard, and a reconciliation to the accounts report that says how complete the data is.

## Who uses it
| User | Question | Tab |
|---|---|---|
| Management | Are we up or down, and why? | Overview |
| Sales manager | Who buys, who is slipping, who has no owner? | Customers |
| Planning / production | What product mix and rates? | Products |
| Operations / customer service | What is open, what is late, are we on time? | Orders & delivery |
| Data owner | Can I trust it? | Data |

## Scope and what is *not* covered
- **Covered:** orders, dispatch/invoicing, customers, items, delivery performance, reconciliation.
- **Not covered:** marketing spend, leads, campaign or channel attribution, pipeline stages, margins and cost. The source data has none of these, so the project does not claim them.

## Data state
History (Jan 2025 – Sep 2026) was rebuilt from dispatch reports, so it covers about 80 % of the accounts-report value for Jan–Aug 2026. From 1 Oct 2026 a single entry workbook becomes the source, with rate, requested date, freight and FX captured on each line. The dashboard is therefore best read as a **trusted picture of customer orders and dispatches**, with the coverage gap stated beside it rather than hidden.
