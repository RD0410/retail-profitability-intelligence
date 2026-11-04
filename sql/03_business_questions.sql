-- 1. How do regions differ in sales, profit, and average discount?
SELECT * FROM v_regional_profitability ORDER BY profit_margin_pct ASC;
-- 2. Which states contribute the most negative realized profit?
SELECT * FROM v_state_risk WHERE profit < 0 ORDER BY profit ASC LIMIT 15;
-- 3. Which subcategories sell well but return weak profit?
SELECT category, subcategory, ROUND(SUM(sales),2) sales,
       ROUND(SUM(profit),2) profit,
       ROUND(100.0*SUM(profit)/NULLIF(SUM(sales),0),2) margin_pct
FROM sales_lines GROUP BY category,subcategory ORDER BY profit ASC;
-- 4. Which discount bands coincide with negative profit?
SELECT * FROM v_discount_performance ORDER BY discount_band;
-- 5. What changed over time?
SELECT month, ROUND(SUM(sales),2) sales, ROUND(SUM(profit),2) profit
FROM sales_lines GROUP BY month ORDER BY month;
