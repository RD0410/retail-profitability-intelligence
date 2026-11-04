# Data dictionary and KPI definitions

The source is Tableau's fictitious Superstore sample, with line-level orders (not a production system). See the README for attribution.

| Field | Type | Description |
|---|---|---|
| `row_id` | Text | Unique order-line key |
| `order_id` | Text | Order identifier, repeated across order lines |
| `customer_id` | Text | Customer identifier, may appear in several orders |
| `order_date`, `ship_date` | ISO date | Dates standardized during ingestion |
| `region`, `state` | Text | Geographic labels |
| `category`, `subcategory` | Text | Product hierarchy |
| `segment` | Text | Customer segment from the source |
| `sales` | Decimal | Recorded sales amount for a line |
| `profit` | Decimal | Recorded realized profit on that line |
| `discount` | Decimal 0–1 | Source discount fraction (0.2 means 20%) |
| `quantity` | Integer | Units in order line |
| `year`, `month` | Integer, YYYY-MM | Derived order period |
| `discount_band` | Text | 0%, <10%, 10–19%, 20–29%, 30%+ |
| `loss_flag` | Integer 0/1 | Whether row's profit is negative |

## Metric rules

- **Sales** = `SUM(sales)`.
- **Profit** = `SUM(profit)`.
- **Profit margin** = `SUM(profit) / SUM(sales)` (sales weighted; never AVG of row margins).
- **Orders** = `COUNT(DISTINCT order_id)` on the actual filter scope. Regional counts cannot be summed if the same order crosses groups.
- **Average discount** = `AVG(discount)` across *order lines*, not sales weighted.
- **Loss exposure** = `SUM(CASE WHEN profit < 0 THEN -profit ELSE 0 END)` (absolute negative line profits; it is not predicted loss).
- **Scenario** = loss exposure × hypothetical recovery assumption – intervention cost.

Source data cover 2014–2017 for this particular archived CSV. Other Superstore versions can differ.
