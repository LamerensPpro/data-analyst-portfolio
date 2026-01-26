-- Evolution du CA mensuel

WITH monthly_sales AS (
    SELECT 
        strftime('%Y-%m', o.order_purchase_timestamp) AS month, -- Mois YYYY-MM
        SUM(oi.price + oi.freight_value) AS revenue --Total CA

    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
)
SELECT 
    month,
    revenue, -- CA 
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue, -- CA M-1
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 2) AS growth_pct -- % Variation CA
FROM monthly_sales;

--Top 10 produits par CA avec catégorie
SELECT 
    p.product_category_name,
    p.product_id,
    COUNT(DISTINCT oi.order_id) AS nb_commandes,
    SUM(oi.price) AS revenue,
    ROUND(AVG(oi.price), 2) AS avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY 
    p.product_category_name,
    p.product_id
ORDER BY revenue DESC
LIMIT 10;