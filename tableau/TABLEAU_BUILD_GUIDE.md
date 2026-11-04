# Tableau build guide | Retail Profitability Intelligence

**Use the cleaned row-level CSV for consistent cross-filters.** After running `python3 -m src.pipeline`, connect Tableau Desktop Free Edition to:

`data/processed/retail_clean.csv` → **Text File** → drag the table onto the canvas.

This project is different from the retention dashboard: the central question is **profit leakage**, not churn. A single clean source supports the following six worksheets and one finished dashboard.

## First, check data types

| Source field | Tableau type | Role |
|---|---|---|
| `order_id` | String | Dimension |
| `order_date` | Date | Dimension |
| `month` | String (YYYY-MM) | Dimension |
| `region`, `state`, `category`, `subcategory`, `segment` | String | Dimension |
| `sales`, `profit`, `discount` | Decimal number | Measure |
| `year` | Whole number (or string, used as filter) | Dimension |
| `loss_flag` | Whole number | Measure |

> **Important:** The customer IDs/order IDs can repeat over multiple lines. Use `COUNTD([order_id])` for unique orders. The sample contains 9,994 line items and 5,009 orders.

## Create these calculated fields (Analysis → Create Calculated Field)

| Name | Tableau formula | Format |
|---|---|---|
| `Profit Margin` | `IF SUM([sales]) = 0 THEN 0 ELSE SUM([profit]) / SUM([sales]) END` | Percentage, 2 decimals |
| `Order Count` | `COUNTD([order_id])` | Whole number |
| `Negative Profit Exposure` | `SUM(IF [profit] < 0 THEN -[profit] ELSE 0 END)` | Currency |
| `Avg Discount` | `AVG([discount])` | Percentage, 1 decimal |

The first two fields are **aggregated** measures and should not be wrapped in another `SUM`.

## Suggested 6-sheet dashboard

1. **KPI · Sales**: drag `sales` to Text; ensure `SUM`, currency ($2,297,200.86 baseline).
2. **KPI · Profit**: drag `profit` to Text; ensure `SUM`, currency ($286,397.02).
3. **KPI · Profit Margin**: drag `Profit Margin` to Text (12.47% baseline).
4. **KPI · Orders**: drag `Order Count` to Text (5,009 baseline).
5. **Profit by Region**: `region` → Rows, `Profit Margin` → Columns, Marks → Bar, sort descending. Add labels; baseline West 14.94%, East 13.48%, South 11.93%, Central 7.92%.
6. **Loss-making Product Lines**: `subcategory` → Rows, `SUM(profit)` → Columns, Marks → Bar, sort ascending, color by positive/negative values. Tables (–$17.73K) and Bookcases (–$3.47K) should be visibly negative.

**Optional seventh worksheet: Discount band diagnostic.** `discount_band` → Columns, `Profit Margin` → Rows, Marks → Bar. Use descriptive title `Observed margin by discount band`, never `Impact of discounts`.

## Assemble

- Dashboard → New Dashboard → Size: fixed **1250 × 850**.
- Background `#F3F7FA`, navy header `#0C293B`, teal accent `#167F89`, muted red for loss-making marks `#C6595F`.
- Vertical container: header → horizontal KPI container → horizontal chart container → optional discount diagnostic and business insight text → source footer.
- Keep all KPI cards similarly sized and use **Fit → Entire View** on each chart if Tableau scrollbars appear.
- Add **Filters** for `region`, `category`, and `year`; apply to **All Using This Data Source** for consistent cross-filtering.
- Optionally set Region chart to **Use as Filter** and test clearing selections.
- Footer: `Source: Tableau Sample — Superstore (fictional) | Historical 2014–2017 sample | Observational analysis`.
- Save as `tableau/Retail_Profitability_Intelligence.twbx` if your Tableau edition supports packaged workbooks; otherwise save `.twb` with linked CSV. Save a screenshot to `tableau/dashboard_final.png`.

## Checks before you publish

- With no filters, verify sales **$2,297,200.86**, profit **$286,397.02**, margin **12.47%**, orders **5,009**.
- Do not SUM the already-aggregated `Profit Margin`; use the calc as written.
- Clear all filters and verify the original totals return.
- If you are using Tableau's installed Sample - Superstore instead of this CSV, baseline numbers may differ across sample versions. For consistency, use the provided cleaned CSV.
- Do not label the what-if recovery scenario as actual profit gained.
