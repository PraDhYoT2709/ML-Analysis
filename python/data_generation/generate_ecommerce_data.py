"""
E-Commerce Synthetic Data Generator
==================================

This script generates realistic synthetic e-commerce data for analytics and machine learning projects.
The data includes customers, products, orders, reviews, and web sessions with realistic relationships
and patterns that mirror real-world e-commerce behavior.

Key Features:
- Generates correlated customer behavior patterns
- Creates seasonal sales trends
- Implements realistic product ratings and reviews
- Includes customer segmentation patterns (RFM analysis ready)
- Generates web analytics data
- Creates marketing campaign attribution

Author: Data Analytics Portfolio Project
Date: 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import json
import os
from typing import Dict, List, Tuple

# Initialize Faker for generating realistic fake data
fake = Faker()
Faker.seed(42)  # Set seed for reproducibility
np.random.seed(42)
random.seed(42)

class EcommerceDataGenerator:
    """
    A comprehensive class for generating synthetic e-commerce data.
    
    This class creates interconnected datasets that represent a realistic
    e-commerce business with customers, products, orders, and analytics data.
    """
    
    def __init__(self, num_customers: int = 10000, num_products: int = 500):
        """
        Initialize the data generator with specified dataset sizes.
        
        Args:
            num_customers (int): Number of customers to generate
            num_products (int): Number of products to generate
        """
        self.num_customers = num_customers
        self.num_products = num_products
        
        # Define realistic product categories and their characteristics
        self.categories = {
            'Electronics': {'avg_price': 299, 'std_price': 200, 'brands': ['Apple', 'Samsung', 'Sony', 'LG', 'Dell']},
            'Clothing': {'avg_price': 79, 'std_price': 40, 'brands': ['Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo']},
            'Books': {'avg_price': 24, 'std_price': 15, 'brands': ['Penguin', 'Random House', 'Oxford', 'Cambridge', 'Wiley']},
            'Home & Garden': {'avg_price': 89, 'std_price': 60, 'brands': ['IKEA', 'Home Depot', 'Wayfair', 'Target', 'Walmart']},
            'Sports': {'avg_price': 149, 'std_price': 80, 'brands': ['Nike', 'Adidas', 'Under Armour', 'Puma', 'Reebok']},
            'Beauty': {'avg_price': 45, 'std_price': 25, 'brands': ['L\'Oreal', 'Maybelline', 'MAC', 'Sephora', 'Ulta']}
        }
        
        # Define marketing channels and their characteristics
        self.marketing_channels = {
            'Google Ads': {'cost_per_click': 2.50, 'conversion_rate': 0.08},
            'Facebook Ads': {'cost_per_click': 1.80, 'conversion_rate': 0.06},
            'Email Marketing': {'cost_per_click': 0.10, 'conversion_rate': 0.15},
            'Organic Search': {'cost_per_click': 0.00, 'conversion_rate': 0.12},
            'Direct': {'cost_per_click': 0.00, 'conversion_rate': 0.20},
            'Referral': {'cost_per_click': 0.50, 'conversion_rate': 0.10}
        }
        
        # Initialize data containers
        self.customers_df = None
        self.products_df = None
        self.orders_df = None
        self.order_items_df = None
        self.reviews_df = None
        self.sessions_df = None
        self.campaigns_df = None
        self.segments_df = None
        
    def generate_customers(self) -> pd.DataFrame:
        """
        Generate realistic customer data with demographics and acquisition information.
        
        Returns:
            pd.DataFrame: Customer data with demographics and registration info
        """
        print("🔄 Generating customer data...")
        
        customers_data = []
        
        for i in range(self.num_customers):
            # Generate basic demographics with realistic distributions
            gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.48, 0.50, 0.02])
            
            # Age distribution that reflects typical online shopping demographics
            age = int(np.random.normal(35, 12))  # Normal distribution around 35 years
            age = max(18, min(80, age))  # Clamp between 18-80
            
            # Registration date with higher probability of recent registrations
            days_ago = int(np.random.exponential(365))  # Exponential decay for registration recency
            days_ago = min(days_ago, 1095)  # Max 3 years ago
            registration_date = datetime.now() - timedelta(days=days_ago)
            
            # Birth date based on age
            birth_year = datetime.now().year - age
            date_of_birth = fake.date_of_birth(minimum_age=age, maximum_age=age)
            
            # Acquisition channel with realistic distribution
            acquisition_channel = np.random.choice(
                list(self.marketing_channels.keys()),
                p=[0.25, 0.20, 0.15, 0.20, 0.15, 0.05]  # Weighted by typical channel performance
            )
            
            customer = {
                'customer_id': i + 1,
                'email': fake.email(),
                'first_name': fake.first_name_male() if gender == 'Male' else fake.first_name_female(),
                'last_name': fake.last_name(),
                'date_of_birth': date_of_birth,
                'gender': gender,
                'phone': fake.phone_number(),
                'address_line1': fake.street_address(),
                'address_line2': fake.secondary_address() if random.random() < 0.3 else None,
                'city': fake.city(),
                'state': fake.state(),
                'country': 'United States',  # Simplified to US for consistency
                'postal_code': fake.zipcode(),
                'registration_date': registration_date,
                'last_login': registration_date + timedelta(days=random.randint(0, 30)),
                'acquisition_channel': acquisition_channel,
                'customer_status': np.random.choice(['active', 'inactive'], p=[0.85, 0.15])
            }
            
            customers_data.append(customer)
        
        self.customers_df = pd.DataFrame(customers_data)
        print(f"✅ Generated {len(self.customers_df)} customers")
        return self.customers_df
    
    def generate_products(self) -> pd.DataFrame:
        """
        Generate product catalog with realistic pricing and category distribution.
        
        Returns:
            pd.DataFrame: Product catalog with pricing and inventory data
        """
        print("🔄 Generating product data...")
        
        products_data = []
        
        for i in range(self.num_products):
            # Select category with realistic distribution
            category = np.random.choice(
                list(self.categories.keys()),
                p=[0.20, 0.25, 0.15, 0.15, 0.15, 0.10]  # Electronics and Clothing are most popular
            )
            
            category_info = self.categories[category]
            
            # Generate realistic pricing based on category
            base_price = np.random.normal(category_info['avg_price'], category_info['std_price'])
            base_price = max(5, base_price)  # Minimum price of $5
            
            # Cost price is typically 40-70% of selling price
            cost_multiplier = np.random.uniform(0.4, 0.7)
            cost_price = base_price * cost_multiplier
            
            # Select brand from category-appropriate brands
            brand = np.random.choice(category_info['brands'])
            
            # Generate product attributes
            product = {
                'product_id': i + 1,
                'product_name': f"{brand} {fake.catch_phrase()} {category[:-1] if category.endswith('s') else category}",
                'category_name': category,
                'brand': brand,
                'unit_price': round(base_price, 2),
                'cost_price': round(cost_price, 2),
                'weight': round(np.random.lognormal(1, 0.5), 2),  # Log-normal for realistic weight distribution
                'color': np.random.choice(['Black', 'White', 'Red', 'Blue', 'Green', 'Gray', 'Brown']),
                'size': np.random.choice(['XS', 'S', 'M', 'L', 'XL', 'XXL', 'One Size']),
                'stock_quantity': np.random.randint(0, 1000),
                'reorder_level': np.random.randint(10, 50),
                'is_active': np.random.choice([True, False], p=[0.9, 0.1]),
                'launch_date': fake.date_between(start_date='-2y', end_date='today')
            }
            
            products_data.append(product)
        
        self.products_df = pd.DataFrame(products_data)
        print(f"✅ Generated {len(self.products_df)} products")
        return self.products_df
    
    def generate_marketing_campaigns(self) -> pd.DataFrame:
        """
        Generate marketing campaign data with budgets and targeting.
        
        Returns:
            pd.DataFrame: Marketing campaign information
        """
        print("🔄 Generating marketing campaigns...")
        
        campaign_types = ['Seasonal Sale', 'Product Launch', 'Brand Awareness', 'Retargeting', 'Holiday Special']
        campaigns_data = []
        
        # Generate 50 campaigns over the past 2 years
        for i in range(50):
            start_date = fake.date_between(start_date='-2y', end_date='-1m')
            duration_days = np.random.randint(7, 90)  # Campaigns run 1 week to 3 months
            end_date = start_date + timedelta(days=duration_days)
            
            campaign_type = np.random.choice(campaign_types)
            channel = np.random.choice(list(self.marketing_channels.keys()))
            
            # Budget varies by channel and campaign type
            base_budget = np.random.lognormal(8, 1)  # Log-normal distribution for realistic budget spread
            budget = min(base_budget, 100000)  # Cap at $100k
            
            campaign = {
                'campaign_id': i + 1,
                'campaign_name': f"{campaign_type} - {channel} - {start_date.strftime('%b %Y')}",
                'campaign_type': campaign_type,
                'channel': channel,
                'start_date': start_date,
                'end_date': end_date,
                'budget': round(budget, 2),
                'target_audience': f"Age {np.random.randint(18, 65)}-{np.random.randint(25, 75)}, {np.random.choice(['All', 'Male', 'Female'])}",
                'campaign_status': 'completed' if end_date < datetime.now().date() else 'active'
            }
            
            campaigns_data.append(campaign)
        
        self.campaigns_df = pd.DataFrame(campaigns_data)
        print(f"✅ Generated {len(self.campaigns_df)} marketing campaigns")
        return self.campaigns_df
    
    def generate_orders(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate order data with realistic purchasing patterns and seasonality.
        
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Orders and order items dataframes
        """
        print("🔄 Generating order data...")
        
        if self.customers_df is None or self.products_df is None:
            raise ValueError("Must generate customers and products before orders")
        
        orders_data = []
        order_items_data = []
        order_id = 1
        
        # Create customer purchasing propensity (some customers buy more than others)
        customer_propensity = np.random.pareto(1, self.num_customers)  # Pareto distribution for realistic buying patterns
        customer_propensity = customer_propensity / customer_propensity.max()  # Normalize to 0-1
        
        for customer_idx, customer in self.customers_df.iterrows():
            customer_id = customer['customer_id']
            registration_date = pd.to_datetime(customer['registration_date'])
            
            # Number of orders based on customer propensity and time since registration
            days_since_registration = (datetime.now() - registration_date).days
            base_order_probability = customer_propensity[customer_idx] * min(days_since_registration / 365, 2)
            
            # Expected number of orders (Poisson distribution)
            num_orders = np.random.poisson(base_order_probability * 5)  # Average 5 orders for high-propensity customers
            num_orders = min(num_orders, 50)  # Cap at 50 orders per customer
            
            if num_orders == 0:
                continue  # Some customers never purchase
            
            # Generate orders for this customer
            for _ in range(num_orders):
                # Order date between registration and now, with seasonal bias
                days_range = (datetime.now() - registration_date).days
                if days_range <= 0:
                    continue
                
                # Add seasonal bias (higher sales in Nov-Dec)
                order_days_ago = np.random.randint(0, days_range)
                order_date = datetime.now() - timedelta(days=order_days_ago)
                
                # Seasonal multiplier (higher in Q4)
                month = order_date.month
                seasonal_multiplier = 1.5 if month in [11, 12] else 1.2 if month in [3, 4, 5] else 1.0
                
                # Skip some orders based on seasonal patterns
                if np.random.random() > seasonal_multiplier * 0.3:
                    continue
                
                # Order characteristics
                payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay', 'Google Pay']
                payment_method = np.random.choice(payment_methods, p=[0.45, 0.25, 0.15, 0.08, 0.07])
                
                order_status_options = ['completed', 'shipped', 'processing', 'cancelled', 'refunded']
                order_status = np.random.choice(order_status_options, p=[0.75, 0.15, 0.05, 0.03, 0.02])
                
                # Campaign attribution (some orders come from campaigns)
                campaign_id = None
                if self.campaigns_df is not None and np.random.random() < 0.3:  # 30% of orders attributed to campaigns
                    active_campaigns = self.campaigns_df[
                        (pd.to_datetime(self.campaigns_df['start_date']) <= order_date) &
                        (pd.to_datetime(self.campaigns_df['end_date']) >= order_date)
                    ]
                    if not active_campaigns.empty:
                        campaign_id = np.random.choice(active_campaigns['campaign_id'].values)
                
                # Generate order items (1-5 items per order)
                num_items = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03])
                selected_products = self.products_df.sample(n=num_items, replace=False)
                
                total_amount = 0
                order_items_for_this_order = []
                
                for _, product in selected_products.iterrows():
                    quantity = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
                    unit_price = product['unit_price']
                    
                    # Apply occasional discounts
                    discount = 0
                    if np.random.random() < 0.15:  # 15% chance of discount
                        discount = np.random.uniform(0.05, 0.3) * unit_price  # 5-30% discount
                    
                    total_price = (unit_price - discount) * quantity
                    total_amount += total_price
                    
                    order_item = {
                        'order_item_id': len(order_items_data) + 1,
                        'order_id': order_id,
                        'product_id': product['product_id'],
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': round(total_price, 2),
                        'discount_applied': round(discount * quantity, 2)
                    }
                    
                    order_items_for_this_order.append(order_item)
                
                # Calculate taxes and shipping
                tax_rate = 0.08  # 8% tax rate
                tax_amount = total_amount * tax_rate
                
                shipping_cost = 0 if total_amount > 50 else np.random.uniform(5, 15)  # Free shipping over $50
                
                discount_amount = sum(item['discount_applied'] for item in order_items_for_this_order)
                final_total = total_amount + tax_amount + shipping_cost
                
                # Create order record
                order = {
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'order_date': order_date,
                    'order_status': order_status,
                    'total_amount': round(final_total, 2),
                    'discount_amount': round(discount_amount, 2),
                    'tax_amount': round(tax_amount, 2),
                    'shipping_cost': round(shipping_cost, 2),
                    'payment_method': payment_method,
                    'shipping_address_line1': customer['address_line1'],
                    'shipping_city': customer['city'],
                    'shipping_state': customer['state'],
                    'shipping_country': customer['country'],
                    'shipping_postal_code': customer['postal_code'],
                    'campaign_id': campaign_id,
                    'coupon_code': f"SAVE{np.random.randint(5, 25)}" if discount_amount > 0 else None,
                    'order_source': np.random.choice(['Website', 'Mobile App', 'Phone'], p=[0.6, 0.35, 0.05]),
                    'delivery_date': order_date + timedelta(days=np.random.randint(1, 10)) if order_status in ['completed', 'shipped'] else None
                }
                
                orders_data.append(order)
                order_items_data.extend(order_items_for_this_order)
                order_id += 1
        
        self.orders_df = pd.DataFrame(orders_data)
        self.order_items_df = pd.DataFrame(order_items_data)
        
        print(f"✅ Generated {len(self.orders_df)} orders with {len(self.order_items_df)} order items")
        return self.orders_df, self.order_items_df
    
    def generate_reviews(self) -> pd.DataFrame:
        """
        Generate product reviews with realistic rating distributions and text.
        
        Returns:
            pd.DataFrame: Product reviews and ratings
        """
        print("🔄 Generating review data...")
        
        if self.orders_df is None or self.order_items_df is None:
            raise ValueError("Must generate orders before reviews")
        
        reviews_data = []
        
        # Only a subset of order items get reviewed (typically 10-30%)
        reviewable_items = self.order_items_df.sample(frac=0.2)  # 20% of items get reviewed
        
        review_templates = {
            5: ["Excellent product!", "Love it!", "Perfect quality", "Highly recommend", "Amazing value"],
            4: ["Good product", "Satisfied with purchase", "Nice quality", "Would buy again", "Pretty good"],
            3: ["It's okay", "Average product", "Could be better", "Not bad", "Decent quality"],
            2: ["Disappointed", "Poor quality", "Not as expected", "Would not recommend", "Waste of money"],
            1: ["Terrible!", "Worst purchase ever", "Complete garbage", "Awful quality", "Don't buy this"]
        }
        
        for _, item in reviewable_items.iterrows():
            # Get order information
            order = self.orders_df[self.orders_df['order_id'] == item['order_id']].iloc[0]
            
            # Only completed orders can have reviews
            if order['order_status'] != 'completed':
                continue
            
            # Rating follows a realistic distribution (skewed towards positive)
            rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.15, 0.35, 0.37])
            
            # Review date is after delivery date
            review_date = pd.to_datetime(order['delivery_date']) + timedelta(days=np.random.randint(1, 60))
            
            # Generate review text
            review_text = np.random.choice(review_templates[rating])
            if np.random.random() < 0.3:  # 30% chance of longer review
                review_text += f" {fake.sentence()}"
            
            review = {
                'review_id': len(reviews_data) + 1,
                'customer_id': order['customer_id'],
                'product_id': item['product_id'],
                'order_id': order['order_id'],
                'rating': rating,
                'review_text': review_text,
                'review_date': review_date,
                'is_verified_purchase': True,  # All our reviews are from verified purchases
                'helpful_votes': np.random.poisson(2) if rating >= 4 else np.random.poisson(0.5),
                'total_votes': np.random.poisson(3) if rating >= 4 else np.random.poisson(1)
            }
            
            reviews_data.append(review)
        
        self.reviews_df = pd.DataFrame(reviews_data)
        print(f"✅ Generated {len(self.reviews_df)} product reviews")
        return self.reviews_df
    
    def generate_website_sessions(self) -> pd.DataFrame:
        """
        Generate website session data for web analytics.
        
        Returns:
            pd.DataFrame: Website session and user behavior data
        """
        print("🔄 Generating website session data...")
        
        if self.customers_df is None:
            raise ValueError("Must generate customers before sessions")
        
        sessions_data = []
        session_id = 1
        
        # Generate sessions for each customer (some customers have many sessions, others few)
        for _, customer in self.customers_df.iterrows():
            customer_id = customer['customer_id']
            registration_date = pd.to_datetime(customer['registration_date'])
            
            # Number of sessions varies by customer engagement
            num_sessions = np.random.negative_binomial(5, 0.3)  # Creates realistic session distribution
            num_sessions = min(num_sessions, 200)  # Cap at 200 sessions
            
            for _ in range(num_sessions):
                # Session date between registration and now
                days_range = (datetime.now() - registration_date).days
                if days_range <= 0:
                    continue
                
                session_start = registration_date + timedelta(days=np.random.randint(0, days_range))
                
                # Session duration (log-normal distribution for realistic web behavior)
                duration_seconds = int(np.random.lognormal(5, 1))  # Average ~3 minutes
                duration_seconds = min(duration_seconds, 7200)  # Cap at 2 hours
                
                session_end = session_start + timedelta(seconds=duration_seconds)
                
                # Page views correlate with session duration
                page_views = max(1, int(duration_seconds / 60) + np.random.poisson(1))
                page_views = min(page_views, 50)  # Cap at 50 page views
                
                # Traffic sources with realistic distribution
                traffic_sources = ['Organic Search', 'Direct', 'Social Media', 'Email', 'Paid Search', 'Referral']
                traffic_source = np.random.choice(traffic_sources, p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
                
                # Device and browser data
                devices = ['Desktop', 'Mobile', 'Tablet']
                device_type = np.random.choice(devices, p=[0.45, 0.50, 0.05])
                
                browsers = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Other']
                browser = np.random.choice(browsers, p=[0.65, 0.20, 0.08, 0.05, 0.02])
                
                operating_systems = ['Windows', 'macOS', 'iOS', 'Android', 'Linux']
                os = np.random.choice(operating_systems, p=[0.40, 0.25, 0.15, 0.15, 0.05])
                
                # Conversion (did they make a purchase?)
                # Check if this customer has orders around this time
                customer_orders = self.orders_df[
                    (self.orders_df['customer_id'] == customer_id) &
                    (pd.to_datetime(self.orders_df['order_date']).dt.date == session_start.date())
                ]
                conversion = len(customer_orders) > 0
                
                # Bounce rate (single page view sessions)
                bounce = page_views == 1
                
                session = {
                    'session_id': session_id,
                    'customer_id': customer_id,
                    'session_start': session_start,
                    'session_end': session_end,
                    'page_views': page_views,
                    'bounce_rate': bounce,
                    'traffic_source': traffic_source,
                    'device_type': device_type,
                    'browser': browser,
                    'operating_system': os,
                    'country': customer['country'],
                    'conversion': conversion,
                    'session_duration': duration_seconds
                }
                
                sessions_data.append(session)
                session_id += 1
        
        self.sessions_df = pd.DataFrame(sessions_data)
        print(f"✅ Generated {len(self.sessions_df)} website sessions")
        return self.sessions_df
    
    def generate_customer_segments(self) -> pd.DataFrame:
        """
        Generate customer segmentation data based on RFM analysis and predictive metrics.
        
        Returns:
            pd.DataFrame: Customer segments with RFM scores and predictions
        """
        print("🔄 Generating customer segmentation data...")
        
        if self.customers_df is None or self.orders_df is None:
            raise ValueError("Must generate customers and orders before segments")
        
        segments_data = []
        
        # Calculate RFM metrics for each customer
        current_date = datetime.now()
        
        for _, customer in self.customers_df.iterrows():
            customer_id = customer['customer_id']
            
            # Get customer's orders
            customer_orders = self.orders_df[
                (self.orders_df['customer_id'] == customer_id) &
                (self.orders_df['order_status'] == 'completed')
            ]
            
            if len(customer_orders) == 0:
                continue  # Skip customers with no completed orders
            
            # Calculate RFM metrics
            last_order_date = pd.to_datetime(customer_orders['order_date']).max()
            recency_days = (current_date - last_order_date).days
            frequency = len(customer_orders)
            monetary = customer_orders['total_amount'].sum()
            
            # RFM Scores (1-5 scale)
            # Recency Score (lower days = higher score)
            if recency_days <= 30:
                recency_score = 5
            elif recency_days <= 60:
                recency_score = 4
            elif recency_days <= 90:
                recency_score = 3
            elif recency_days <= 180:
                recency_score = 2
            else:
                recency_score = 1
            
            # Frequency Score
            if frequency >= 10:
                frequency_score = 5
            elif frequency >= 6:
                frequency_score = 4
            elif frequency >= 4:
                frequency_score = 3
            elif frequency >= 2:
                frequency_score = 2
            else:
                frequency_score = 1
            
            # Monetary Score
            if monetary >= 2000:
                monetary_score = 5
            elif monetary >= 1000:
                monetary_score = 4
            elif monetary >= 500:
                monetary_score = 3
            elif monetary >= 200:
                monetary_score = 2
            else:
                monetary_score = 1
            
            # Determine segment based on RFM scores
            if recency_score >= 4 and frequency_score >= 4 and monetary_score >= 4:
                segment_name = 'Champions'
            elif recency_score >= 3 and frequency_score >= 3 and monetary_score >= 3:
                segment_name = 'Loyal Customers'
            elif recency_score >= 4 and frequency_score <= 2:
                segment_name = 'New Customers'
            elif recency_score >= 3 and frequency_score >= 2 and monetary_score <= 2:
                segment_name = 'Potential Loyalists'
            elif recency_score <= 2 and frequency_score >= 3 and monetary_score >= 3:
                segment_name = 'At Risk'
            elif recency_score <= 2 and frequency_score >= 2 and monetary_score >= 2:
                segment_name = 'Cannot Lose Them'
            elif recency_score <= 2 and frequency_score <= 2:
                segment_name = 'Hibernating'
            else:
                segment_name = 'Others'
            
            # Predict Customer Lifetime Value (simplified model)
            avg_order_value = monetary / frequency
            days_between_orders = recency_days / frequency if frequency > 1 else recency_days
            predicted_orders_per_year = 365 / max(days_between_orders, 30)  # Minimum 30 days between orders
            predicted_lifespan_years = min(frequency * 0.5, 5)  # Estimate based on current behavior
            
            clv_prediction = avg_order_value * predicted_orders_per_year * predicted_lifespan_years
            
            # Churn Probability (based on recency and behavior patterns)
            if recency_days > 365:
                churn_probability = 0.9
            elif recency_days > 180:
                churn_probability = 0.7
            elif recency_days > 90:
                churn_probability = 0.4
            elif recency_days > 30:
                churn_probability = 0.2
            else:
                churn_probability = 0.1
            
            # Adjust churn probability based on frequency and monetary value
            if frequency >= 5 and monetary >= 1000:
                churn_probability *= 0.5  # Loyal high-value customers less likely to churn
            
            segment = {
                'segment_id': len(segments_data) + 1,
                'customer_id': customer_id,
                'segment_name': segment_name,
                'segment_description': f"RFM: {recency_score}{frequency_score}{monetary_score}",
                'rfm_score': f"{recency_score}{frequency_score}{monetary_score}",
                'recency_score': recency_score,
                'frequency_score': frequency_score,
                'monetary_score': monetary_score,
                'clv_prediction': round(clv_prediction, 2),
                'churn_probability': round(churn_probability, 4),
                'segment_date': current_date.date()
            }
            
            segments_data.append(segment)
        
        self.segments_df = pd.DataFrame(segments_data)
        print(f"✅ Generated {len(self.segments_df)} customer segments")
        return self.segments_df
    
    def save_data(self, output_dir: str = "/workspace/data/synthetic") -> None:
        """
        Save all generated datasets to CSV files.
        
        Args:
            output_dir (str): Directory to save the CSV files
        """
        print(f"💾 Saving data to {output_dir}...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save all datasets
        datasets = {
            'customers.csv': self.customers_df,
            'products.csv': self.products_df,
            'orders.csv': self.orders_df,
            'order_items.csv': self.order_items_df,
            'reviews.csv': self.reviews_df,
            'website_sessions.csv': self.sessions_df,
            'marketing_campaigns.csv': self.campaigns_df,
            'customer_segments.csv': self.segments_df
        }
        
        for filename, df in datasets.items():
            if df is not None:
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False)
                print(f"  📄 Saved {filename} ({len(df)} rows)")
        
        # Save data summary
        self.save_data_summary(output_dir)
        
    def save_data_summary(self, output_dir: str) -> None:
        """
        Save a summary of the generated data for documentation.
        
        Args:
            output_dir (str): Directory to save the summary file
        """
        summary = {
            'generation_date': datetime.now().isoformat(),
            'datasets': {},
            'key_metrics': {},
            'data_quality_notes': []
        }
        
        # Dataset summaries
        datasets = {
            'customers': self.customers_df,
            'products': self.products_df,
            'orders': self.orders_df,
            'order_items': self.order_items_df,
            'reviews': self.reviews_df,
            'website_sessions': self.sessions_df,
            'marketing_campaigns': self.campaigns_df,
            'customer_segments': self.segments_df
        }
        
        for name, df in datasets.items():
            if df is not None:
                summary['datasets'][name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                }
        
        # Key business metrics
        if self.orders_df is not None and self.customers_df is not None:
            total_revenue = self.orders_df[self.orders_df['order_status'] == 'completed']['total_amount'].sum()
            avg_order_value = self.orders_df[self.orders_df['order_status'] == 'completed']['total_amount'].mean()
            customers_with_orders = len(self.orders_df['customer_id'].unique())
            
            summary['key_metrics'] = {
                'total_revenue': round(total_revenue, 2),
                'average_order_value': round(avg_order_value, 2),
                'customers_with_orders': customers_with_orders,
                'conversion_rate': round(customers_with_orders / len(self.customers_df) * 100, 2)
            }
        
        # Data quality notes
        summary['data_quality_notes'] = [
            "All data is synthetically generated for demonstration purposes",
            "Customer emails and personal information are fake",
            "Product names and descriptions are generated",
            "Order patterns include realistic seasonality and customer behavior",
            "RFM segmentation follows industry standard practices",
            "Churn probability calculations are simplified for demonstration"
        ]
        
        # Save summary as JSON
        summary_path = os.path.join(output_dir, 'data_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"  📊 Saved data_summary.json")
    
    def generate_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Generate all datasets in the correct order.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of all generated datasets
        """
        print("🚀 Starting comprehensive e-commerce data generation...")
        print(f"📊 Target: {self.num_customers:,} customers, {self.num_products:,} products")
        
        # Generate data in dependency order
        self.generate_customers()
        self.generate_products()
        self.generate_marketing_campaigns()
        self.generate_orders()
        self.generate_reviews()
        self.generate_website_sessions()
        self.generate_customer_segments()
        
        # Save all data
        self.save_data()
        
        print("✅ Data generation completed successfully!")
        
        return {
            'customers': self.customers_df,
            'products': self.products_df,
            'orders': self.orders_df,
            'order_items': self.order_items_df,
            'reviews': self.reviews_df,
            'sessions': self.sessions_df,
            'campaigns': self.campaigns_df,
            'segments': self.segments_df
        }

def main():
    """
    Main function to run the data generation process.
    """
    print("=" * 60)
    print("🏪 E-COMMERCE DATA GENERATOR")
    print("=" * 60)
    
    # Initialize generator with desired dataset sizes
    generator = EcommerceDataGenerator(
        num_customers=10000,  # Generate 10,000 customers
        num_products=500      # Generate 500 products
    )
    
    # Generate all data
    datasets = generator.generate_all_data()
    
    # Print final statistics
    print("\n📈 GENERATION SUMMARY")
    print("-" * 30)
    for name, df in datasets.items():
        if df is not None:
            print(f"{name.capitalize()}: {len(df):,} records")
    
    print(f"\n💾 All data saved to: /workspace/data/synthetic/")
    print("🎉 Ready for analysis!")

if __name__ == "__main__":
    main()