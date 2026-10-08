-- 1. Monthly business health
SELECT
    order_month,
    order_count,
    active_customers,
    ROUND(gmv, 2) AS gmv,
    ROUND(avg_order_value, 2) AS avg_order_value,
    ROUND(avg_delivery_days, 2) AS avg_delivery_days,
    ROUND(late_delivery_rate * 100, 2) AS late_delivery_rate_pct
FROM monthly_kpi
ORDER BY order_month;

-- 2. Repeat-purchase rate at the customer level
WITH customer_orders AS (
    SELECT customer_unique_id, COUNT(DISTINCT order_id) AS order_count
    FROM fact_orders
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*) AS customer_count,
    SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_purchase_rate_pct
FROM customer_orders;

-- 3. Payment-method performance
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(payment_value), 2) AS gmv,
    ROUND(AVG(payment_value), 2) AS avg_order_value,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM fact_orders
GROUP BY payment_type
ORDER BY gmv DESC;

-- 4. Regions needing delivery investigation
SELECT
    customer_state,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    ROUND(100.0 * AVG(CASE WHEN delivery_delay_days > 0 THEN 1.0 ELSE 0.0 END), 2) AS late_delivery_rate_pct
FROM fact_orders
GROUP BY customer_state
HAVING COUNT(DISTINCT order_id) >= 100
ORDER BY late_delivery_rate_pct DESC, avg_delivery_days DESC;
