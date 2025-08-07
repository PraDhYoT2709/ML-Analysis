"""
Simple Customer Segmentation
============================

Uses K-means clustering to segment customers into actionable business groups.
Focus on interpretability and business value over complexity.

Author: Data Analytics Portfolio Project
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

class SimpleCustomerSegmentation:
    """
    Simple customer segmentation using K-means clustering.
    
    Creates business-relevant customer segments based on:
    - Purchase behavior (frequency, recency, monetary value)
    - Customer demographics
    - Engagement patterns
    """
    
    def __init__(self):
        """Initialize the segmentation model and load data."""
        print("Loading customer data for segmentation...")
        
        # Load generated data
        self.customers = pd.read_csv('/workspace/data/customers.csv')
        self.products = pd.read_csv('/workspace/data/products.csv')
        self.orders = pd.read_csv('/workspace/data/orders.csv')
        
        # Convert date columns
        self.customers['registration_date'] = pd.to_datetime(self.customers['registration_date'])
        self.orders['order_date'] = pd.to_datetime(self.orders['order_date'])
        
        print(f"Data loaded: {len(self.customers)} customers, {len(self.orders)} orders")
        
        # Create customer features
        self.customer_features = None
        self.segments = None
        
    def create_customer_features(self):
        """
        Create features for customer segmentation.
        
        Features include:
        - RFM metrics (Recency, Frequency, Monetary)
        - Customer demographics
        - Engagement indicators
        """
        print("\n🔧 Creating customer features for segmentation...")
        
        # Calculate order summary per customer
        order_summary = self.orders.groupby('customer_id').agg({
            'order_id': 'count',           # Frequency
            'total_amount': ['sum', 'mean'], # Monetary
            'order_date': ['min', 'max']    # For recency calculation
        }).reset_index()
        
        # Flatten column names
        order_summary.columns = ['customer_id', 'total_orders', 'total_spent', 
                               'avg_order_value', 'first_order_date', 'last_order_date']
        
        # Merge with customer data
        customer_features = self.customers.merge(order_summary, on='customer_id', how='left')
        
        # Fill NaN values for customers with no orders
        customer_features['total_orders'] = customer_features['total_orders'].fillna(0)
        customer_features['total_spent'] = customer_features['total_spent'].fillna(0)
        customer_features['avg_order_value'] = customer_features['avg_order_value'].fillna(0)
        
        # Calculate recency (days since last order)
        customer_features['days_since_last_order'] = (
            pd.Timestamp.now() - customer_features['last_order_date']
        ).dt.days
        customer_features['days_since_last_order'] = customer_features['days_since_last_order'].fillna(999)  # High value for no orders
        
        # Calculate customer tenure (days since registration)
        customer_features['customer_tenure_days'] = (
            pd.Timestamp.now() - customer_features['registration_date']
        ).dt.days
        
        # Create binary features for channels
        for channel in self.customers['acquisition_channel'].unique():
            customer_features[f'channel_{channel.lower().replace(" ", "_")}'] = (
                customer_features['acquisition_channel'] == channel
            ).astype(int)
        
        # Create gender binary feature
        customer_features['is_male'] = (customer_features['gender'] == 'Male').astype(int)
        
        # Select features for clustering
        feature_columns = [
            'age',
            'total_orders',
            'total_spent', 
            'avg_order_value',
            'days_since_last_order',
            'customer_tenure_days',
            'is_male'
        ]
        
        # Add channel features
        channel_features = [col for col in customer_features.columns if col.startswith('channel_')]
        feature_columns.extend(channel_features)
        
        self.customer_features = customer_features
        self.feature_columns = feature_columns
        
        print(f"✅ Created {len(feature_columns)} features for {len(customer_features)} customers")
        
        # Display feature summary
        print("\n📊 Feature Summary:")
        for feature in feature_columns[:7]:  # Show first 7 features
            if feature in customer_features.columns:
                mean_val = customer_features[feature].mean()
                print(f"  {feature}: mean = {mean_val:.1f}")
    
    def find_optimal_clusters(self, max_clusters=8):
        """
        Find the optimal number of clusters using silhouette analysis.
        
        Args:
            max_clusters (int): Maximum number of clusters to test
            
        Returns:
            int: Optimal number of clusters
        """
        print(f"\n🔍 Finding optimal number of clusters (testing 2-{max_clusters})...")
        
        # Prepare data for clustering
        X = self.customer_features[self.feature_columns].copy()
        
        # Standardize features (important for K-means)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Test different numbers of clusters
        silhouette_scores = []
        cluster_range = range(2, max_clusters + 1)
        
        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            
            print(f"  {n_clusters} clusters: silhouette score = {silhouette_avg:.3f}")
        
        # Find optimal number of clusters
        optimal_clusters = cluster_range[np.argmax(silhouette_scores)]
        best_score = max(silhouette_scores)
        
        print(f"\n✅ Optimal number of clusters: {optimal_clusters} (score: {best_score:.3f})")
        
        self.scaler = scaler
        self.X_scaled = X_scaled
        
        return optimal_clusters
    
    def perform_clustering(self, n_clusters=None):
        """
        Perform K-means clustering on customer data.
        
        Args:
            n_clusters (int): Number of clusters. If None, finds optimal number.
        """
        if n_clusters is None:
            n_clusters = self.find_optimal_clusters()
        
        print(f"\n🎯 Performing K-means clustering with {n_clusters} clusters...")
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(self.X_scaled)
        
        # Add cluster labels to customer data
        self.customer_features['cluster'] = cluster_labels
        
        # Calculate cluster statistics
        cluster_summary = self.customer_features.groupby('cluster').agg({
            'customer_id': 'count',
            'age': 'mean',
            'total_orders': 'mean',
            'total_spent': 'mean',
            'avg_order_value': 'mean',
            'days_since_last_order': 'mean',
            'customer_tenure_days': 'mean'
        }).round(1)
        
        cluster_summary.columns = ['customer_count', 'avg_age', 'avg_orders', 
                                 'avg_total_spent', 'avg_order_value', 
                                 'avg_days_since_last_order', 'avg_tenure_days']
        
        self.cluster_summary = cluster_summary
        self.kmeans_model = kmeans
        
        print(f"✅ Clustering completed!")
        
        return cluster_labels
    
    def assign_business_names(self):
        """
        Assign business-meaningful names to clusters based on characteristics.
        """
        print(f"\n🏷️  Assigning business names to clusters...")
        
        cluster_names = {}
        
        for cluster_id, row in self.cluster_summary.iterrows():
            avg_orders = row['avg_orders']
            avg_spent = row['avg_total_spent']
            avg_recency = row['avg_days_since_last_order']
            
            # Business logic for naming segments
            if avg_orders >= 3 and avg_spent >= 200 and avg_recency <= 60:
                name = "VIP Customers"
            elif avg_orders >= 2 and avg_recency <= 30:
                name = "Loyal Customers"
            elif avg_orders >= 1 and avg_recency <= 90:
                name = "Regular Customers"
            elif avg_orders == 0:
                name = "Inactive Customers"
            elif avg_recency > 180:
                name = "At-Risk Customers"
            else:
                name = "Occasional Buyers"
            
            cluster_names[cluster_id] = name
        
        # Add business names to data
        self.customer_features['segment_name'] = self.customer_features['cluster'].map(cluster_names)
        self.cluster_summary['segment_name'] = [cluster_names[i] for i in self.cluster_summary.index]
        
        self.cluster_names = cluster_names
        
        print("✅ Business segment names assigned!")
    
    def analyze_segments(self):
        """
        Analyze and display segment characteristics.
        """
        print(f"\n" + "="*50)
        print("CUSTOMER SEGMENT ANALYSIS")
        print("="*50)
        
        # Display segment summary
        for cluster_id, row in self.cluster_summary.iterrows():
            segment_name = self.cluster_names[cluster_id]
            customer_count = row['customer_count']
            percentage = (customer_count / len(self.customer_features)) * 100
            
            print(f"\n📊 {segment_name} (Cluster {cluster_id})")
            print(f"  Size: {customer_count} customers ({percentage:.1f}%)")
            print(f"  Average age: {row['avg_age']:.1f} years")
            print(f"  Average orders: {row['avg_orders']:.1f}")
            print(f"  Average total spent: ${row['avg_total_spent']:.2f}")
            print(f"  Average order value: ${row['avg_order_value']:.2f}")
            print(f"  Days since last order: {row['avg_days_since_last_order']:.0f}")
            print(f"  Customer tenure: {row['avg_tenure_days']:.0f} days")
        
        # Channel analysis by segment
        print(f"\n📱 Channel Distribution by Segment:")
        channel_segment = self.customer_features.groupby(['segment_name', 'acquisition_channel']).size().unstack(fill_value=0)
        
        for segment in channel_segment.index:
            print(f"\n  {segment}:")
            segment_total = channel_segment.loc[segment].sum()
            for channel in channel_segment.columns:
                count = channel_segment.loc[segment, channel]
                pct = (count / segment_total) * 100 if segment_total > 0 else 0
                print(f"    {channel}: {count} ({pct:.1f}%)")
    
    def generate_business_recommendations(self):
        """
        Generate specific business recommendations for each segment.
        """
        print(f"\n" + "="*50)
        print("BUSINESS RECOMMENDATIONS")
        print("="*50)
        
        recommendations = {}
        
        for cluster_id, segment_name in self.cluster_names.items():
            row = self.cluster_summary.loc[cluster_id]
            customer_count = row['customer_count']
            avg_spent = row['avg_total_spent']
            avg_recency = row['avg_days_since_last_order']
            
            recs = []
            
            if segment_name == "VIP Customers":
                recs.extend([
                    "🌟 Implement VIP loyalty program with exclusive benefits",
                    "📞 Assign dedicated customer success managers",
                    "🎁 Offer early access to new products",
                    "💎 Create premium product recommendations"
                ])
                
            elif segment_name == "Loyal Customers":
                recs.extend([
                    "🏆 Reward loyalty with points-based program",
                    "📧 Send personalized product recommendations",
                    "🎯 Target with cross-selling campaigns",
                    "📊 Monitor for potential upgrade to VIP"
                ])
                
            elif segment_name == "Regular Customers":
                recs.extend([
                    "📈 Focus on increasing order frequency",
                    "💰 Offer bundle deals to increase order value",
                    "📱 Engage through targeted email campaigns",
                    "🔄 Create repeat purchase incentives"
                ])
                
            elif segment_name == "At-Risk Customers":
                recs.extend([
                    "🚨 Immediate win-back campaign with discounts",
                    "📞 Proactive outreach to understand issues",
                    "🎁 Special offers to re-engage",
                    "📊 Monitor closely for churn prevention"
                ])
                
            elif segment_name == "Inactive Customers":
                recs.extend([
                    "📧 Reactivation email campaign series",
                    "💸 Aggressive discount offers (20-30% off)",
                    "🎯 Retargeting ads on social media",
                    "📋 Survey to understand barriers to purchase"
                ])
                
            elif segment_name == "Occasional Buyers":
                recs.extend([
                    "🎯 Targeted campaigns to increase frequency",
                    "📱 Mobile app engagement initiatives",
                    "🔔 Reminder campaigns for repeat purchases",
                    "💡 Educational content about product benefits"
                ])
            
            recommendations[segment_name] = recs
            
            # Display recommendations
            print(f"\n🎯 {segment_name} ({customer_count} customers)")
            for rec in recs:
                print(f"  {rec}")
        
        self.recommendations = recommendations
    
    def calculate_business_impact(self):
        """
        Calculate potential business impact of segmentation strategies.
        """
        print(f"\n" + "="*50)
        print("BUSINESS IMPACT PROJECTION")
        print("="*50)
        
        total_revenue = self.orders['total_amount'].sum()
        
        print(f"💰 Current Business Metrics:")
        print(f"  Total customers: {len(self.customer_features):,}")
        print(f"  Total revenue: ${total_revenue:,.2f}")
        print(f"  Average revenue per customer: ${total_revenue/len(self.customer_features):.2f}")
        
        # Impact projections by segment
        impact_projections = {}
        total_projected_impact = 0
        
        for cluster_id, segment_name in self.cluster_names.items():
            row = self.cluster_summary.loc[cluster_id]
            customer_count = row['customer_count']
            current_avg_spent = row['avg_total_spent']
            
            # Conservative improvement estimates based on segment
            if segment_name == "VIP Customers":
                improvement = 0.05  # 5% increase
                confidence = "High"
            elif segment_name == "Loyal Customers":
                improvement = 0.10  # 10% increase
                confidence = "High"
            elif segment_name == "Regular Customers":
                improvement = 0.15  # 15% increase
                confidence = "Medium"
            elif segment_name == "At-Risk Customers":
                improvement = 0.25  # 25% recovery
                confidence = "Medium"
            elif segment_name == "Inactive Customers":
                improvement = 0.05  # 5% reactivation
                confidence = "Low"
            else:  # Occasional Buyers
                improvement = 0.20  # 20% increase
                confidence = "Medium"
            
            projected_revenue_increase = customer_count * current_avg_spent * improvement
            total_projected_impact += projected_revenue_increase
            
            impact_projections[segment_name] = {
                'customers': customer_count,
                'current_avg_spent': current_avg_spent,
                'improvement': improvement,
                'projected_increase': projected_revenue_increase,
                'confidence': confidence
            }
            
            print(f"\n📈 {segment_name}:")
            print(f"  Customers: {customer_count:,}")
            print(f"  Current avg spent: ${current_avg_spent:.2f}")
            print(f"  Projected improvement: {improvement*100:.0f}%")
            print(f"  Revenue increase: ${projected_revenue_increase:,.2f}")
            print(f"  Confidence: {confidence}")
        
        print(f"\n🎯 TOTAL PROJECTED IMPACT:")
        print(f"  Annual revenue increase: ${total_projected_impact:,.2f}")
        print(f"  Percentage of current revenue: {(total_projected_impact/total_revenue)*100:.1f}%")
        
        roi_percentage = (total_projected_impact / total_revenue) * 100
        if roi_percentage > 10:
            print(f"  💡 STRONG ROI POTENTIAL: {roi_percentage:.1f}% revenue increase")
        elif roi_percentage > 5:
            print(f"  ✅ GOOD ROI POTENTIAL: {roi_percentage:.1f}% revenue increase")
        else:
            print(f"  📊 MODERATE ROI POTENTIAL: {roi_percentage:.1f}% revenue increase")
    
    def run_complete_segmentation(self):
        """
        Run the complete customer segmentation workflow.
        """
        print("🎯 SIMPLE CUSTOMER SEGMENTATION")
        print("Creating actionable customer segments for business growth...")
        
        # Run complete workflow
        self.create_customer_features()
        self.perform_clustering()
        self.assign_business_names()
        self.analyze_segments()
        self.generate_business_recommendations()
        self.calculate_business_impact()
        
        print(f"\n✅ Customer segmentation completed!")
        print(f"🎯 {len(self.cluster_names)} actionable customer segments created")
        print(f"📊 Business recommendations generated for each segment")

def main():
    """
    Main function to run customer segmentation.
    """
    segmentation = SimpleCustomerSegmentation()
    segmentation.run_complete_segmentation()

if __name__ == "__main__":
    main()