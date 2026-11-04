-- Weighted margin, not an average of line-level profit margins.
CREATE VIEW v_regional_profitability AS
SELECT region, COUNT(*) AS order_lines, COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(sales),2) AS sales, ROUND(SUM(profit),2) AS profit,
       ROUND(100.0*SUM(profit)/NULLIF(SUM(sales),0),2) AS profit_margin_pct,
       ROUND(100.0*AVG(discount),2) AS avg_line_discount_pct
FROM sales_lines GROUP BY region;

CREATE VIEW v_state_risk AS
SELECT region, state, ROUND(SUM(sales),2) AS sales,
       ROUND(SUM(profit),2) AS profit,
       ROUND(100.0*SUM(profit)/NULLIF(SUM(sales),0),2) AS profit_margin_pct,
       ROUND(100.0*AVG(discount),2) AS avg_line_discount_pct,
       SUM(loss_flag) AS loss_lines
FROM sales_lines GROUP BY region,state;

CREATE VIEW v_discount_performance AS
SELECT discount_band, COUNT(*) AS order_lines,
       ROUND(SUM(sales),2) AS sales, ROUND(SUM(profit),2) AS profit,
       ROUND(100.0*SUM(profit)/NULLIF(SUM(sales),0),2) AS margin_pct
FROM sales_lines GROUP BY discount_band;
