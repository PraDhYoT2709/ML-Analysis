-- Simple Customer Analytics SQL
-- =============================
-- Essential SQL queries for business insights
-- Demonstrates: JOINs, aggregations, window functions, and business logic

-- Query 1: Customer Overview and Segmentation
-- Purpose: Understand customer base and identify key segments
-- Skills: JOINs, aggregations, CASE statements, window functions

WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.age,
        c.gender,
        c.acquisition_channel,
        c.registration_date,
        
        -- Order metrics
        COUNT(o.order_id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        
        -- Recency (days since last order)
        CASE 
            WHEN MAX(o.order_date) IS NULL THEN 999
            ELSE EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date))
        END as days_since_last_order,
        
        -- Customer lifespan
        CASE 
            WHEN MAX(o.order_date) IS NOT NULL THEN
                EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) + 1
            ELSE 0
        END as customer_lifespan_days
        
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.age, c.gender, c.acquisition_channel, c.registration_date
),

-- Customer segmentation based on RFM-like analysis
customer_segments AS (
    SELECT *,
        -- Simple customer segmentation
        CASE 
            WHEN total_orders = 0 THEN 'Inactive'
            WHEN total_orders = 1 AND days_since_last_order > 90 THEN 'One-Time Buyer'
            WHEN total_orders >= 5 AND total_spent >= 300 THEN 'VIP Customer'
            WHEN total_orders >= 2 AND days_since_last_order <= 30 THEN 'Loyal Customer'
            WHEN days_since_last_order > 90 THEN 'At Risk'
            ELSE 'Regular Customer'
        END as customer_segment,
        
        -- Percentile rankings
        PERCENT_RANK() OVER (ORDER BY total_spent) as spending_percentile,
        PERCENT_RANK() OVER (ORDER BY total_orders) as frequency_percentile
        
    FROM customer_metrics
)

SELECT 
    customer_segment,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage,
    ROUND(AVG(total_spent), 2) as avg_total_spent,
    ROUND(AVG(avg_order_value), 2) as avg_order_value,
    ROUND(AVG(total_orders), 1) as avg_orders_per_customer
FROM customer_segments
GROUP BY customer_segment
ORDER BY avg_total_spent DESC;

-- Query 2: Monthly Revenue Trends
-- Purpose: Understand business performance over time
-- Skills: Date functions, aggregations, window functions

SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(SUM(total_amount), 2) as monthly_revenue,
    ROUND(AVG(total_amount), 2) as avg_order_value,
    
    -- Month-over-month growth
    ROUND(
        (SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', order_date))) 
        / LAG(SUM(total_amount)) OVER (ORDER BY DATE_TRUNC('month', order_date)) * 100, 
        1
    ) as mom_revenue_growth_pct
    
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Query 3: Product Category Performance
-- Purpose: Identify best-performing product categories
-- Skills: JOINs, aggregations, rankings

WITH category_performance AS (
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) as total_orders,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        ROUND(SUM(o.total_amount), 2) as total_revenue,
        ROUND(AVG(o.total_amount), 2) as avg_order_value,
        ROUND(AVG(p.price), 2) as avg_product_price,
        
        -- Revenue per product in category
        ROUND(SUM(o.total_amount) / COUNT(DISTINCT p.product_id), 2) as revenue_per_product
        
    FROM products p
    JOIN orders o ON p.product_id IN (
        -- This is a simplified join assuming orders contain product info
        -- In a real schema, you'd have an order_items table
        SELECT product_id FROM products WHERE category = p.category LIMIT 1
    )
    GROUP BY p.category
)

SELECT 
    category,
    total_orders,
    unique_customers,
    total_revenue,
    avg_order_value,
    avg_product_price,
    revenue_per_product,
    
    -- Category rankings
    RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
    RANK() OVER (ORDER BY total_orders DESC) as order_volume_rank
    
FROM category_performance
ORDER BY total_revenue DESC;

-- Query 4: Customer Acquisition Channel Analysis
-- Purpose: Evaluate marketing channel effectiveness
-- Skills: Aggregations, conditional logic, percentages

SELECT 
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) as total_customers,
    COUNT(DISTINCT o.customer_id) as customers_with_orders,
    
    -- Conversion rate (customers who made at least one order)
    ROUND(
        COUNT(DISTINCT o.customer_id) * 100.0 / COUNT(DISTINCT c.customer_id), 
        1
    ) as conversion_rate_pct,
    
    -- Revenue metrics
    COALESCE(SUM(o.total_amount), 0) as total_revenue,
    ROUND(COALESCE(AVG(o.total_amount), 0), 2) as avg_order_value,
    
    -- Revenue per customer (including non-buyers)
    ROUND(
        COALESCE(SUM(o.total_amount), 0) / COUNT(DISTINCT c.customer_id), 
        2
    ) as revenue_per_customer,
    
    -- Average orders per customer
    ROUND(
        COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id), 
        1
    ) as avg_orders_per_customer
    
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.acquisition_channel
ORDER BY total_revenue DESC;

-- Query 5: Customer Lifetime Value Analysis
-- Purpose: Identify high-value customers and predict CLV
-- Skills: Complex calculations, window functions, conditional logic

WITH customer_clv AS (
    SELECT 
        c.customer_id,
        c.age,
        c.acquisition_channel,
        c.registration_date,
        
        -- Basic metrics
        COUNT(o.order_id) as total_orders,
        COALESCE(SUM(o.total_amount), 0) as total_spent,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        
        -- Time-based metrics
        MIN(o.order_date) as first_order_date,
        MAX(o.order_date) as last_order_date,
        
        -- Customer lifespan and frequency
        CASE 
            WHEN COUNT(o.order_id) > 1 AND MAX(o.order_date) != MIN(o.order_date) THEN
                EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) / NULLIF(COUNT(o.order_id) - 1, 0)
            ELSE NULL
        END as avg_days_between_orders,
        
        -- Predicted CLV (simple model: avg_order_value * predicted_future_orders)
        CASE 
            WHEN COUNT(o.order_id) >= 2 THEN
                COALESCE(AVG(o.total_amount), 0) * 
                (COUNT(o.order_id) * 2)  -- Simple prediction: double current order count
            WHEN COUNT(o.order_id) = 1 THEN
                COALESCE(AVG(o.total_amount), 0) * 1.5  -- Assume 1.5 more orders
            ELSE 0
        END as predicted_clv
        
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.age, c.acquisition_channel, c.registration_date
)

SELECT 
    -- CLV segments
    CASE 
        WHEN predicted_clv >= 500 THEN 'High Value (500+)'
        WHEN predicted_clv >= 200 THEN 'Medium Value (200-499)'
        WHEN predicted_clv >= 50 THEN 'Low Value (50-199)'
        ELSE 'Minimal Value (<50)'
    END as clv_segment,
    
    COUNT(*) as customer_count,
    ROUND(AVG(predicted_clv), 2) as avg_predicted_clv,
    ROUND(AVG(total_spent), 2) as avg_current_spent,
    ROUND(AVG(total_orders), 1) as avg_orders,
    ROUND(AVG(avg_order_value), 2) as avg_order_value
    
FROM customer_clv
GROUP BY 
    CASE 
        WHEN predicted_clv >= 500 THEN 'High Value (500+)'
        WHEN predicted_clv >= 200 THEN 'Medium Value (200-499)'
        WHEN predicted_clv >= 50 THEN 'Low Value (50-199)'
        ELSE 'Minimal Value (<50)'
    END
ORDER BY avg_predicted_clv DESC;

-- Query 6: At-Risk Customer Identification
-- Purpose: Find customers likely to churn for retention campaigns
-- Skills: Date calculations, conditional logic, rankings

SELECT 
    c.customer_id,
    c.age,
    c.acquisition_channel,
    COUNT(o.order_id) as total_orders,
    ROUND(SUM(o.total_amount), 2) as total_spent,
    MAX(o.order_date) as last_order_date,
    EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) as days_since_last_order,
    
    -- Risk score (higher = more at risk)
    CASE 
        WHEN EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 180 THEN 'High Risk'
        WHEN EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 90 THEN 'Medium Risk'
        WHEN EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 30 THEN 'Low Risk'
        ELSE 'Active'
    END as churn_risk,
    
    -- Retention priority (high-value at-risk customers)
    CASE 
        WHEN SUM(o.total_amount) >= 200 AND EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 90 
        THEN 'High Priority'
        WHEN SUM(o.total_amount) >= 100 AND EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 60 
        THEN 'Medium Priority'
        ELSE 'Low Priority'
    END as retention_priority
    
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.age, c.acquisition_channel
HAVING COUNT(o.order_id) >= 1  -- Only customers with at least one order
   AND EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) > 30  -- Haven't ordered in 30+ days
ORDER BY total_spent DESC, days_since_last_order DESC
LIMIT 50;  -- Top 50 at-risk customers

-- Business Summary Query
-- Purpose: Key metrics for executive dashboard
-- Skills: Multiple aggregations, percentages, business KPIs

SELECT 
    'Business Overview' as metric_category,
    
    -- Customer metrics
    (SELECT COUNT(*) FROM customers) as total_customers,
    (SELECT COUNT(DISTINCT customer_id) FROM orders) as customers_with_orders,
    
    -- Order metrics  
    (SELECT COUNT(*) FROM orders) as total_orders,
    (SELECT ROUND(SUM(total_amount), 2) FROM orders) as total_revenue,
    (SELECT ROUND(AVG(total_amount), 2) FROM orders) as avg_order_value,
    
    -- Conversion and retention
    ROUND(
        (SELECT COUNT(DISTINCT customer_id) FROM orders) * 100.0 / 
        (SELECT COUNT(*) FROM customers), 1
    ) as customer_conversion_rate_pct,
    
    -- Recent activity (last 30 days)
    (SELECT COUNT(*) FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '30 days') as orders_last_30_days,
    (SELECT ROUND(SUM(total_amount), 2) FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL '30 days') as revenue_last_30_days;