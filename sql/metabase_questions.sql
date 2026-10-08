-- Card 1: Executive KPI cards
SELECT
    COUNT(DISTINCT order_id) AS delivered_orders,
    COUNT(DISTINCT customer_unique_id) AS purchasing_customers,
    ROUND(SUM(payment_value), 2) AS gmv,
    ROUND(AVG(payment_value), 2) AS avg_order_value,
    ROUND(100.0 * AVG(CASE WHEN delivery_delay_days > 0 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct
FROM fact_orders;

-- Card 2: Monthly GMV and orders trend
SELECT
    order_month,
    order_count,
    ROUND(gmv, 2) AS gmv,
    ROUND(avg_order_value, 2) AS avg_order_value
FROM monthly_kpi
ORDER BY order_month;

-- Card 3: Customer repeat-purchase rate
WITH customer_orders AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS order_count
    FROM fact_orders
    GROUP BY customer_unique_id
)
SELECT
    CASE WHEN order_count = 1 THEN 'One-time buyer' ELSE 'Repeat buyer' END AS customer_type,
    COUNT(*) AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS customer_share_pct
FROM customer_orders
GROUP BY customer_type
ORDER BY customers DESC;

-- Card 4: Cohort retention heatmap
SELECT
    cohort_month,
    cohort_index,
    cohort_size,
    active_customers,
    ROUND(retention_rate * 100, 2) AS retention_rate_pct
FROM cohort_retention
ORDER BY cohort_month, cohort_index;

-- Card 5: Top categories by allocated GMV
SELECT
    product_category_name,
    order_count,
    item_count,
    ROUND(allocated_gmv, 2) AS allocated_gmv,
    ROUND(avg_item_price, 2) AS avg_item_price
FROM category_kpi
ORDER BY allocated_gmv DESC
LIMIT 10;

-- Card 6: Delivery-risk states (minimum 100 delivered orders)
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(100.0 * AVG(CASE WHEN delivery_delay_days > 0 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct
FROM fact_orders
GROUP BY customer_state
HAVING COUNT(DISTINCT order_id) >= 100
ORDER BY late_delivery_rate_pct DESC, avg_delivery_days DESC;
