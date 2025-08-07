"""
Simple E-Commerce Data Generator
===============================

Creates basic customer and sales data for analytics demonstration.
Focus on clarity and business relevance over complexity.

Author: Data Analytics Portfolio Project
Date: 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

class SimpleDataGenerator:
    """
    Generate basic e-commerce data for customer analytics.
    
    Creates three main datasets:
    - Customers: Basic demographic and registration info
    - Products: Simple product catalog with categories
    - Orders: Purchase transactions linking customers to products
    """
    
    def __init__(self, num_customers=1000, num_products=50):
        """
        Initialize the data generator.
        
        Args:
            num_customers (int): Number of customers to generate (default: 1000)
            num_products (int): Number of products to generate (default: 50)
        """
        self.num_customers = num_customers
        self.num_products = num_products
        
        # Business parameters
        self.categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']
        self.channels = ['Website', 'Mobile App', 'Social Media', 'Email', 'Referral']
        
    def generate_customers(self):
        """
        Generate customer data with basic demographics.
        
        Returns:
            pd.DataFrame: Customer data with ID, demographics, and registration info
        """
        print("Generating customer data...")
        
        customers = []
        
        for i in range(1, self.num_customers + 1):
            # Basic demographics
            age = int(np.random.normal(35, 12))  # Average age 35, std 12
            age = max(18, min(80, age))  # Keep realistic age range
            
            gender = np.random.choice(['Male', 'Female'], p=[0.48, 0.52])
            
            # Registration date (more recent customers)
            days_ago = int(np.random.exponential(180))  # Average 6 months ago
            registration_date = datetime.now() - timedelta(days=days_ago)
            
            # Acquisition channel
            channel = np.random.choice(self.channels, p=[0.3, 0.25, 0.2, 0.15, 0.1])
            
            customer = {
                'customer_id': i,
                'age': age,
                'gender': gender,
                'registration_date': registration_date.strftime('%Y-%m-%d'),
                'acquisition_channel': channel,
                'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'customer_status': 'Active'
            }
            
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_products(self):
        """
        Generate product catalog with categories and pricing.
        
        Returns:
            pd.DataFrame: Product data with categories, names, and prices
        """
        print("Generating product data...")
        
        products = []
        
        # Category-based pricing (average prices)
        category_prices = {
            'Electronics': (150, 80),   # mean, std
            'Clothing': (45, 25),
            'Books': (15, 8),
            'Home': (60, 40),
            'Sports': (80, 50)
        }
        
        for i in range(1, self.num_products + 1):
            category = np.random.choice(self.categories)
            mean_price, std_price = category_prices[category]
            
            # Generate realistic price
            price = np.random.normal(mean_price, std_price)
            price = max(5, round(price, 2))  # Minimum $5
            
            product = {
                'product_id': i,
                'product_name': f"{category} Product {i}",
                'category': category,
                'price': price,
                'cost': round(price * np.random.uniform(0.4, 0.7), 2),  # 40-70% of price
                'launch_date': (datetime.now() - timedelta(days=np.random.randint(1, 365))).strftime('%Y-%m-%d')
            }
            
            products.append(product)
        
        return pd.DataFrame(products)
    
    def generate_orders(self, customers_df, products_df):
        """
        Generate order transactions based on customer and product data.
        
        Args:
            customers_df (pd.DataFrame): Customer data
            products_df (pd.DataFrame): Product data
            
        Returns:
            pd.DataFrame: Order data with customer purchases
        """
        print("Generating order data...")
        
        orders = []
        order_id = 1
        
        for _, customer in customers_df.iterrows():
            customer_id = customer['customer_id']
            reg_date = datetime.strptime(customer['registration_date'], '%Y-%m-%d')
            
            # Determine number of orders per customer (some customers buy more)
            if np.random.random() < 0.3:  # 30% are frequent buyers
                num_orders = np.random.poisson(5) + 1  # 1-10+ orders
            elif np.random.random() < 0.5:  # 50% are occasional buyers
                num_orders = np.random.poisson(2) + 1  # 1-5 orders
            else:  # 20% are one-time buyers or no orders
                num_orders = np.random.choice([0, 1], p=[0.2, 0.8])
            
            # Generate orders for this customer
            for order_num in range(num_orders):
                # Order date (after registration, more recent orders likely)
                days_after_reg = int(np.random.exponential(60))  # Average 2 months after reg
                order_date = reg_date + timedelta(days=days_after_reg)
                
                # Don't create future orders
                if order_date > datetime.now():
                    continue
                
                # Select products for this order (1-3 items typically)
                num_items = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
                order_products = products_df.sample(n=num_items)
                
                # Calculate order total
                total_amount = order_products['price'].sum()
                
                # Apply occasional discount
                discount = 0
                if np.random.random() < 0.15:  # 15% chance of discount
                    discount = total_amount * np.random.uniform(0.1, 0.25)  # 10-25% off
                
                final_amount = total_amount - discount
                
                order = {
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'order_date': order_date.strftime('%Y-%m-%d'),
                    'total_amount': round(final_amount, 2),
                    'discount_amount': round(discount, 2),
                    'num_items': num_items,
                    'order_status': 'Completed'
                }
                
                orders.append(order)
                order_id += 1
        
        return pd.DataFrame(orders)
    
    def generate_all_data(self):
        """
        Generate complete dataset and save to CSV files.
        
        Returns:
            dict: Dictionary containing all generated dataframes
        """
        print("=" * 50)
        print("SIMPLE E-COMMERCE DATA GENERATION")
        print("=" * 50)
        
        # Generate data
        customers_df = self.generate_customers()
        products_df = self.generate_products()
        orders_df = self.generate_orders(customers_df, products_df)
        
        # Save to CSV files
        print("\nSaving data to CSV files...")
        customers_df.to_csv('/workspace/data/customers.csv', index=False)
        products_df.to_csv('/workspace/data/products.csv', index=False)
        orders_df.to_csv('/workspace/data/orders.csv', index=False)
        
        # Print summary statistics
        print("\n" + "=" * 30)
        print("DATA GENERATION SUMMARY")
        print("=" * 30)
        print(f"Customers generated: {len(customers_df):,}")
        print(f"Products generated: {len(products_df):,}")
        print(f"Orders generated: {len(orders_df):,}")
        print(f"Average orders per customer: {len(orders_df) / len(customers_df):.1f}")
        print(f"Total revenue: ${orders_df['total_amount'].sum():,.2f}")
        print(f"Average order value: ${orders_df['total_amount'].mean():.2f}")
        
        # Customer distribution
        print(f"\nCustomer Age Distribution:")
        print(f"  Average age: {customers_df['age'].mean():.1f} years")
        print(f"  Age range: {customers_df['age'].min()}-{customers_df['age'].max()} years")
        
        # Order patterns
        orders_per_customer = orders_df.groupby('customer_id').size()
        print(f"\nOrder Patterns:")
        print(f"  Customers with 0 orders: {len(customers_df) - len(orders_per_customer):,}")
        print(f"  Customers with 1 order: {(orders_per_customer == 1).sum():,}")
        print(f"  Customers with 2+ orders: {(orders_per_customer >= 2).sum():,}")
        print(f"  Most orders by one customer: {orders_per_customer.max()}")
        
        print("\n✅ Data generation completed successfully!")
        print("📁 Files saved in /workspace/data/")
        
        return {
            'customers': customers_df,
            'products': products_df,
            'orders': orders_df
        }

def main():
    """
    Main function to generate sample e-commerce data.
    """
    # Create data generator
    generator = SimpleDataGenerator(num_customers=1000, num_products=50)
    
    # Generate all data
    data = generator.generate_all_data()
    
    print("\n🎯 Ready for analysis!")
    print("Next steps:")
    print("1. Run SQL analysis: sql/customer_analysis.sql")
    print("2. Statistical analysis: python/statistical_analysis.py") 
    print("3. Customer segmentation: python/customer_segmentation.py")

if __name__ == "__main__":
    main()