-- Advanced Customer Analytics SQL Queries
-- Demonstrates complex SQL techniques for business intelligence

-- =====================================================
-- 1. RFM ANALYSIS (Recency, Frequency, Monetary)
-- =====================================================

WITH customer_rfm AS (
    SELECT 
        c.customer_id,
        c.email,
        c.first_name || ' ' || c.last_name AS customer_name,
        -- Recency: Days since last purchase
        EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) AS recency_days,
        -- Frequency: Number of orders
        COUNT(DISTINCT o.order_id) AS frequency,
        -- Monetary: Total amount spent
        COALESCE(SUM(o.total_amount), 0) AS monetary_value,
        -- Additional metrics
        AVG(o.total_amount) AS avg_order_value,
        MIN(o.order_date) AS first_purchase_date,
        MAX(o.order_date) AS last_purchase_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.customer_status = 'active'
    GROUP BY c.customer_id, c.email, c.first_name, c.last_name
),
rfm_scores AS (
    SELECT *,
        -- Recency Score (1-5, where 5 is most recent)
        CASE 
            WHEN recency_days <= 30 THEN 5
            WHEN recency_days <= 60 THEN 4
            WHEN recency_days <= 90 THEN 3
            WHEN recency_days <= 180 THEN 2
            ELSE 1
        END AS recency_score,
        
        -- Frequency Score (1-5, where 5 is highest frequency)
        CASE 
            WHEN frequency >= 10 THEN 5
            WHEN frequency >= 6 THEN 4
            WHEN frequency >= 4 THEN 3
            WHEN frequency >= 2 THEN 2
            ELSE 1
        END AS frequency_score,
        
        -- Monetary Score (1-5, where 5 is highest value)
        CASE 
            WHEN monetary_value >= 2000 THEN 5
            WHEN monetary_value >= 1000 THEN 4
            WHEN monetary_value >= 500 THEN 3
            WHEN monetary_value >= 200 THEN 2
            ELSE 1
        END AS monetary_score
    FROM customer_rfm
),
customer_segments AS (
    SELECT *,
        CONCAT(recency_score, frequency_score, monetary_score) AS rfm_score,
        CASE 
            WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
            WHEN recency_score >= 3 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'Loyal Customers'
            WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'New Customers'
            WHEN recency_score >= 3 AND frequency_score >= 2 AND monetary_score <= 2 THEN 'Potential Loyalists'
            WHEN recency_score <= 2 AND frequency_score >= 3 AND monetary_score >= 3 THEN 'At Risk'
            WHEN recency_score <= 2 AND frequency_score >= 2 AND monetary_score >= 2 THEN 'Cannot Lose Them'
            WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Hibernating'
            ELSE 'Others'
        END AS customer_segment
    FROM rfm_scores
)
SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage,
    ROUND(AVG(monetary_value), 2) AS avg_monetary_value,
    ROUND(AVG(frequency), 2) AS avg_frequency,
    ROUND(AVG(recency_days), 2) AS avg_recency_days,
    SUM(monetary_value) AS total_revenue
FROM customer_segments
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- =====================================================
-- 2. COHORT ANALYSIS - Customer Retention by Month
-- =====================================================

WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month,
        MIN(order_date) AS first_order_date
    FROM orders
    GROUP BY customer_id
),
order_periods AS (
    SELECT 
        o.customer_id,
        cc.cohort_month,
        DATE_TRUNC('month', o.order_date) AS order_month,
        EXTRACT(YEAR FROM AGE(DATE_TRUNC('month', o.order_date), cc.cohort_month)) * 12 + 
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', o.order_date), cc.cohort_month)) AS period_number
    FROM orders o
    JOIN customer_cohorts cc ON o.customer_id = cc.customer_id
),
cohort_data AS (
    SELECT 
        cohort_month,
        period_number,
        COUNT(DISTINCT customer_id) AS customers_count
    FROM order_periods
    GROUP BY cohort_month, period_number
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
)
SELECT 
    cd.cohort_month,
    cs.cohort_size,
    cd.period_number,
    cd.customers_count,
    ROUND(cd.customers_count * 100.0 / cs.cohort_size, 2) AS retention_rate
FROM cohort_data cd
JOIN cohort_sizes cs ON cd.cohort_month = cs.cohort_month
WHERE cd.period_number <= 12  -- First 12 months
ORDER BY cd.cohort_month, cd.period_number;

-- =====================================================
-- 3. CUSTOMER LIFETIME VALUE PREDICTION
-- =====================================================

WITH customer_metrics AS (
    SELECT 
        c.customer_id,
        c.registration_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM(o.total_amount), 0) AS total_spent,
        COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date,
        EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) + 1 AS customer_lifespan_days,
        CASE 
            WHEN COUNT(DISTINCT o.order_id) > 1 THEN
                EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) / (COUNT(DISTINCT o.order_id) - 1.0)
            ELSE NULL
        END AS avg_days_between_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.customer_status = 'active'
    GROUP BY c.customer_id, c.registration_date
),
clv_calculation AS (
    SELECT *,
        -- Purchase Frequency (orders per year)
        CASE 
            WHEN customer_lifespan_days > 0 THEN
                (total_orders * 365.0) / customer_lifespan_days
            ELSE 0
        END AS purchase_frequency_yearly,
        
        -- Predicted Customer Lifespan (based on order frequency)
        CASE 
            WHEN avg_days_between_orders > 0 THEN
                avg_days_between_orders * total_orders / 365.0 * 2  -- Assume they'll continue for 2x their current pattern
            ELSE 1  -- Default to 1 year for single-order customers
        END AS predicted_lifespan_years,
        
        -- Churn Probability (based on days since last order)
        CASE 
            WHEN EXTRACT(DAYS FROM CURRENT_DATE - last_order_date) > 365 THEN 0.9
            WHEN EXTRACT(DAYS FROM CURRENT_DATE - last_order_date) > 180 THEN 0.7
            WHEN EXTRACT(DAYS FROM CURRENT_DATE - last_order_date) > 90 THEN 0.4
            WHEN EXTRACT(DAYS FROM CURRENT_DATE - last_order_date) > 30 THEN 0.2
            ELSE 0.1
        END AS churn_probability
    FROM customer_metrics
)
SELECT 
    customer_id,
    total_orders,
    ROUND(total_spent, 2) AS total_spent,
    ROUND(avg_order_value, 2) AS avg_order_value,
    ROUND(purchase_frequency_yearly, 2) AS orders_per_year,
    ROUND(predicted_lifespan_years, 2) AS predicted_lifespan_years,
    ROUND(churn_probability, 3) AS churn_probability,
    -- CLV = Average Order Value × Purchase Frequency × Customer Lifespan × (1 - Churn Probability)
    ROUND(
        avg_order_value * 
        purchase_frequency_yearly * 
        predicted_lifespan_years * 
        (1 - churn_probability), 2
    ) AS predicted_clv,
    CASE 
        WHEN avg_order_value * purchase_frequency_yearly * predicted_lifespan_years * (1 - churn_probability) >= 2000 THEN 'High Value'
        WHEN avg_order_value * purchase_frequency_yearly * predicted_lifespan_years * (1 - churn_probability) >= 1000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS clv_segment
FROM clv_calculation
WHERE total_orders > 0
ORDER BY predicted_clv DESC;

-- =====================================================
-- 4. ADVANCED PRODUCT ANALYSIS WITH WINDOW FUNCTIONS
-- =====================================================

WITH product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        cat.category_name,
        p.brand,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.total_price) AS total_revenue,
        COUNT(DISTINCT oi.order_id) AS order_count,
        AVG(oi.unit_price) AS avg_selling_price,
        AVG(r.rating) AS avg_rating,
        COUNT(r.review_id) AS review_count
    FROM products p
    LEFT JOIN categories cat ON p.category_id = cat.category_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN reviews r ON p.product_id = r.product_id
    GROUP BY p.product_id, p.product_name, cat.category_name, p.brand
),
product_rankings AS (
    SELECT *,
        -- Rankings within category
        ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) as revenue_rank_in_category,
        ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_quantity_sold DESC) as quantity_rank_in_category,
        
        -- Overall rankings
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) as overall_revenue_rank,
        PERCENT_RANK() OVER (ORDER BY total_revenue DESC) as revenue_percentile,
        
        -- Moving averages and comparisons
        AVG(total_revenue) OVER (PARTITION BY category_name) as category_avg_revenue,
        AVG(total_revenue) OVER () as overall_avg_revenue,
        
        -- Revenue contribution
        SUM(total_revenue) OVER (PARTITION BY category_name) as category_total_revenue,
        SUM(total_revenue) OVER () as grand_total_revenue
    FROM product_sales
    WHERE total_revenue > 0
)
SELECT 
    product_name,
    category_name,
    brand,
    ROUND(total_revenue, 2) as total_revenue,
    total_quantity_sold,
    revenue_rank_in_category,
    overall_revenue_rank,
    ROUND(revenue_percentile * 100, 2) as revenue_percentile,
    ROUND(total_revenue / category_total_revenue * 100, 2) as category_revenue_share,
    ROUND(total_revenue / grand_total_revenue * 100, 2) as overall_revenue_share,
    ROUND(avg_rating, 2) as avg_rating,
    review_count,
    CASE 
        WHEN total_revenue > category_avg_revenue * 2 THEN 'Star Product'
        WHEN total_revenue > category_avg_revenue THEN 'Above Average'
        WHEN total_revenue > category_avg_revenue * 0.5 THEN 'Average'
        ELSE 'Underperformer'
    END as performance_category
FROM product_rankings
ORDER BY total_revenue DESC;

-- =====================================================
-- 5. SEASONAL TRENDS AND TIME SERIES ANALYSIS
-- =====================================================

WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) AS month,
        COUNT(DISTINCT order_id) AS orders_count,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(total_amount) AS total_revenue,
        AVG(total_amount) AS avg_order_value
    FROM orders
    WHERE order_status NOT IN ('cancelled', 'refunded')
    GROUP BY DATE_TRUNC('month', order_date)
),
seasonal_analysis AS (
    SELECT *,
        EXTRACT(YEAR FROM month) AS year,
        EXTRACT(MONTH FROM month) AS month_num,
        TO_CHAR(month, 'Month') AS month_name,
        -- Year-over-year growth
        LAG(total_revenue, 12) OVER (ORDER BY month) AS revenue_same_month_last_year,
        -- Month-over-month growth
        LAG(total_revenue, 1) OVER (ORDER BY month) AS revenue_previous_month,
        -- Moving averages
        AVG(total_revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS revenue_3month_avg,
        AVG(total_revenue) OVER (ORDER BY month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS revenue_12month_avg
    FROM monthly_sales
)
SELECT 
    month,
    year,
    month_name,
    ROUND(total_revenue, 2) AS total_revenue,
    orders_count,
    unique_customers,
    ROUND(avg_order_value, 2) AS avg_order_value,
    
    -- Growth calculations
    CASE 
        WHEN revenue_same_month_last_year IS NOT NULL THEN
            ROUND((total_revenue - revenue_same_month_last_year) / revenue_same_month_last_year * 100, 2)
        ELSE NULL
    END AS yoy_growth_percent,
    
    CASE 
        WHEN revenue_previous_month IS NOT NULL THEN
            ROUND((total_revenue - revenue_previous_month) / revenue_previous_month * 100, 2)
        ELSE NULL
    END AS mom_growth_percent,
    
    ROUND(revenue_3month_avg, 2) AS revenue_3month_avg,
    ROUND(revenue_12month_avg, 2) AS revenue_12month_avg,
    
    -- Seasonal indicators
    CASE 
        WHEN month_num IN (11, 12) THEN 'Holiday Season'
        WHEN month_num IN (6, 7, 8) THEN 'Summer'
        WHEN month_num IN (3, 4, 5) THEN 'Spring'
        ELSE 'Regular'
    END AS season
FROM seasonal_analysis
ORDER BY month DESC;

-- =====================================================
-- 6. CUSTOMER CHURN PREDICTION ANALYSIS
-- =====================================================

WITH customer_behavior AS (
    SELECT 
        c.customer_id,
        c.registration_date,
        COUNT(DISTINCT o.order_id) AS total_orders,
        MAX(o.order_date) AS last_order_date,
        MIN(o.order_date) AS first_order_date,
        EXTRACT(DAYS FROM CURRENT_DATE - MAX(o.order_date)) AS days_since_last_order,
        EXTRACT(DAYS FROM MAX(o.order_date) - MIN(o.order_date)) AS customer_lifespan_days,
        AVG(o.total_amount) AS avg_order_value,
        SUM(o.total_amount) AS total_spent,
        STDDEV(o.total_amount) AS order_value_stddev,
        -- Engagement metrics
        COUNT(DISTINCT DATE_TRUNC('month', o.order_date)) AS active_months,
        AVG(EXTRACT(DAYS FROM o.order_date - LAG(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date))) AS avg_days_between_orders
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE c.customer_status = 'active'
    GROUP BY c.customer_id, c.registration_date
),
churn_indicators AS (
    SELECT *,
        -- Churn risk factors
        CASE 
            WHEN days_since_last_order > 365 THEN 'Very High'
            WHEN days_since_last_order > 180 THEN 'High'
            WHEN days_since_last_order > 90 THEN 'Medium'
            WHEN days_since_last_order > 30 THEN 'Low'
            ELSE 'Very Low'
        END AS churn_risk_level,
        
        -- Behavioral patterns
        CASE 
            WHEN total_orders = 1 THEN 'One-time Buyer'
            WHEN total_orders <= 3 THEN 'Infrequent Buyer'
            WHEN total_orders <= 10 THEN 'Regular Buyer'
            ELSE 'Frequent Buyer'
        END AS buyer_type,
        
        -- Value segments
        CASE 
            WHEN total_spent >= 2000 THEN 'High Value'
            WHEN total_spent >= 500 THEN 'Medium Value'
            ELSE 'Low Value'
        END AS value_segment
    FROM customer_behavior
    WHERE total_orders > 0
)
SELECT 
    churn_risk_level,
    buyer_type,
    value_segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(days_since_last_order), 2) AS avg_days_since_last_order,
    ROUND(AVG(total_spent), 2) AS avg_total_spent,
    ROUND(AVG(total_orders), 2) AS avg_total_orders,
    ROUND(SUM(total_spent), 2) AS total_revenue_at_risk
FROM churn_indicators
GROUP BY churn_risk_level, buyer_type, value_segment
ORDER BY 
    CASE churn_risk_level 
        WHEN 'Very High' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 5
    END,
    total_revenue_at_risk DESC;