-- Analyse (Recency, Monetary)

WITH max_date AS ( -- Date max dataset
    SELECT MAX(order_purchase_timestamp) AS last_date
    FROM orders 
),
customer_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_city,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price + oi.freight_value) AS monetary, -- total payé
        julianday((SELECT last_date FROM max_date)) - julianday(MAX(o.order_purchase_timestamp)) AS recency_days -- nombre jour depuis dernière commande en fonction Date max
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_id, c.customer_city
)
SELECT 
    customer_id,
    customer_city,
    --frequency, -- Inutile 1 customer_id pour 1 order_id
    ROUND(monetary, 2) AS monetary,
    recency_days, --Nbre de jours
    NTILE(5) OVER (ORDER BY recency_days) AS recency_score, -- bucket recency
    --NTILE(5) OVER (ORDER BY frequency DESC) AS frequency_score,
    NTILE(5) OVER (ORDER BY monetary DESC) AS monetary_score -- bucket monetary
FROM customer_metrics;

-- Clients achat supérieur à >1000$
SELECT 
    c.customer_id,
    c.customer_city,
    c.customer_state,
    --COUNT(DISTINCT o.order_id) AS nb_orders, -- Inutile 1 customer_id pour 1 order_id
    SUM(oi.price + oi.freight_value) AS total_spent, -- total payé
    AVG(oi.price + oi.freight_value) AS avg_item_price -- Prix moyen par article
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_id, c.customer_city, c.customer_state
HAVING SUM(oi.price + oi.freight_value) > 1000
ORDER BY total_spent DESC;