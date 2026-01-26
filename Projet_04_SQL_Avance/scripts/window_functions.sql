--Classement vendeurs par CA par mois
SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) AS month,
    s.seller_id,
    s.seller_city,
    SUM(oi.price) AS revenue,
    RANK() OVER (PARTITION BY strftime('%Y-%m', o.order_purchase_timestamp) ORDER BY SUM(oi.price) DESC) AS rank_month
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
GROUP BY 
    month,
    s.seller_id,
    s.seller_city;

-- Classement Meilleurs villes d'achat par CA par mois
WITH ranked_cities AS (
SELECT 
    strftime('%Y-%m', o.order_purchase_timestamp) AS month,
    c.customer_city,
    ROUND(SUM(oi.price),2) AS revenue,
    RANK() OVER (PARTITION BY strftime('%Y-%m', o.order_purchase_timestamp) ORDER BY SUM(oi.price) DESC) AS rank_month
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
JOIN customers c ON o.customer_id=c.customer_id
WHERE o.order_status = 'delivered'
GROUP BY 
    month,
    c.customer_city
)
SELECT 
    month,
    customer_city,
    revenue
FROM ranked_cities
WHERE rank_month=1;
