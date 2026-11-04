-- One row per order line; not one row per order.
CREATE TABLE sales_lines (
    row_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    ship_date TEXT NOT NULL,
    ship_mode TEXT,
    customer_id TEXT,
    segment TEXT NOT NULL,
    state TEXT NOT NULL,
    region TEXT NOT NULL,
    product_id TEXT,
    category TEXT NOT NULL,
    subcategory TEXT NOT NULL,
    sales REAL NOT NULL CHECK(sales >= 0),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    discount REAL NOT NULL CHECK(discount BETWEEN 0 AND 1),
    profit REAL NOT NULL,
    year INTEGER NOT NULL,
    month TEXT NOT NULL,
    discount_band TEXT NOT NULL,
    loss_flag INTEGER NOT NULL CHECK(loss_flag IN (0,1))
);
CREATE INDEX idx_sales_month ON sales_lines(month);
CREATE INDEX idx_sales_region ON sales_lines(region);
CREATE INDEX idx_sales_category ON sales_lines(category);
