"""
Simple Statistical Analysis
===========================

Demonstrates key statistical concepts for business decision-making.
Focus on practical applications and clear interpretations.

Author: Data Analytics Portfolio Project
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import ttest_ind, chi2_contingency, pearsonr
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

class SimpleStatisticalAnalyzer:
    """
    Simple statistical analysis for customer behavior insights.
    
    Performs key statistical tests and creates business-relevant insights:
    - Descriptive statistics
    - Hypothesis testing (t-tests, chi-square)
    - Correlation analysis
    - A/B testing simulation
    """
    
    def __init__(self):
        """Initialize the analyzer and load data."""
        print("Loading customer data for analysis...")
        
        # Load generated data
        self.customers = pd.read_csv('/workspace/data/customers.csv')
        self.products = pd.read_csv('/workspace/data/products.csv')
        self.orders = pd.read_csv('/workspace/data/orders.csv')
        
        # Convert date columns
        self.customers['registration_date'] = pd.to_datetime(self.customers['registration_date'])
        self.orders['order_date'] = pd.to_datetime(self.orders['order_date'])
        
        print(f"Data loaded: {len(self.customers)} customers, {len(self.orders)} orders")
        
    def descriptive_analysis(self):
        """
        Perform descriptive statistical analysis.
        
        Analyzes customer demographics and purchase behavior patterns.
        """
        print("\n" + "="*50)
        print("DESCRIPTIVE STATISTICAL ANALYSIS")
        print("="*50)
        
        # Customer age analysis
        print("\n📊 Customer Age Analysis:")
        age_stats = self.customers['age'].describe()
        print(f"  Average age: {age_stats['mean']:.1f} years")
        print(f"  Median age: {age_stats['50%']:.1f} years")
        print(f"  Age range: {age_stats['min']:.0f} - {age_stats['max']:.0f} years")
        print(f"  Standard deviation: {age_stats['std']:.1f} years")
        
        # Order value analysis
        print("\n💰 Order Value Analysis:")
        order_stats = self.orders['total_amount'].describe()
        print(f"  Average order value: ${order_stats['mean']:.2f}")
        print(f"  Median order value: ${order_stats['50%']:.2f}")
        print(f"  Order value range: ${order_stats['min']:.2f} - ${order_stats['max']:.2f}")
        print(f"  Standard deviation: ${order_stats['std']:.2f}")
        
        # Coefficient of variation (measure of relative variability)
        cv = (order_stats['std'] / order_stats['mean']) * 100
        print(f"  Coefficient of variation: {cv:.1f}%")
        
        if cv < 50:
            print("    → Low variability: Consistent order values")
        elif cv < 100:
            print("    → Moderate variability: Some variation in spending")
        else:
            print("    → High variability: Wide range of order values")
        
        # Gender distribution
        print("\n👥 Customer Demographics:")
        gender_dist = self.customers['gender'].value_counts()
        for gender, count in gender_dist.items():
            pct = (count / len(self.customers)) * 100
            print(f"  {gender}: {count} customers ({pct:.1f}%)")
        
        # Channel distribution
        print("\n📱 Acquisition Channels:")
        channel_dist = self.customers['acquisition_channel'].value_counts()
        for channel, count in channel_dist.items():
            pct = (count / len(self.customers)) * 100
            print(f"  {channel}: {count} customers ({pct:.1f}%)")
    
    def hypothesis_testing(self):
        """
        Perform hypothesis testing for business insights.
        
        Tests:
        1. Gender differences in order values
        2. Channel effectiveness differences
        3. Age group spending patterns
        """
        print("\n" + "="*50)
        print("HYPOTHESIS TESTING")
        print("="*50)
        
        # Merge customer and order data for analysis
        customer_orders = self.customers.merge(self.orders, on='customer_id', how='inner')
        
        # Test 1: Gender differences in order values
        print("\n🧪 Test 1: Gender Differences in Order Values")
        print("H0: No difference in average order values between genders")
        print("H1: There is a difference in average order values between genders")
        
        male_orders = customer_orders[customer_orders['gender'] == 'Male']['total_amount']
        female_orders = customer_orders[customer_orders['gender'] == 'Female']['total_amount']
        
        if len(male_orders) > 0 and len(female_orders) > 0:
            # Perform t-test
            t_stat, p_value = ttest_ind(male_orders, female_orders)
            
            print(f"\nResults:")
            print(f"  Male average order value: ${male_orders.mean():.2f} (n={len(male_orders)})")
            print(f"  Female average order value: ${female_orders.mean():.2f} (n={len(female_orders)})")
            print(f"  T-statistic: {t_stat:.3f}")
            print(f"  P-value: {p_value:.4f}")
            
            # Interpret results
            if p_value < 0.05:
                print("  ✅ Significant difference found (p < 0.05)")
                if male_orders.mean() > female_orders.mean():
                    print("  📊 Males have higher average order values")
                else:
                    print("  📊 Females have higher average order values")
            else:
                print("  ❌ No significant difference found (p ≥ 0.05)")
                print("  📊 Gender does not significantly affect order values")
        
        # Test 2: Channel effectiveness
        print("\n🧪 Test 2: Acquisition Channel Effectiveness")
        
        # Calculate conversion rates by channel
        channel_stats = []
        for channel in self.customers['acquisition_channel'].unique():
            channel_customers = self.customers[self.customers['acquisition_channel'] == channel]
            channel_buyers = customer_orders[customer_orders['acquisition_channel'] == channel]['customer_id'].nunique()
            
            conversion_rate = channel_buyers / len(channel_customers)
            avg_order_value = customer_orders[customer_orders['acquisition_channel'] == channel]['total_amount'].mean()
            
            channel_stats.append({
                'channel': channel,
                'total_customers': len(channel_customers),
                'buyers': channel_buyers,
                'conversion_rate': conversion_rate,
                'avg_order_value': avg_order_value if not np.isnan(avg_order_value) else 0
            })
        
        # Display results
        print("\nChannel Performance:")
        for stat in sorted(channel_stats, key=lambda x: x['conversion_rate'], reverse=True):
            print(f"  {stat['channel']}:")
            print(f"    Conversion rate: {stat['conversion_rate']*100:.1f}%")
            print(f"    Avg order value: ${stat['avg_order_value']:.2f}")
            print(f"    Total customers: {stat['total_customers']}")
        
        # Test 3: Age group analysis
        print("\n🧪 Test 3: Age Group Spending Patterns")
        
        # Create age groups
        customer_orders['age_group'] = pd.cut(customer_orders['age'], 
                                            bins=[0, 25, 35, 45, 100], 
                                            labels=['18-25', '26-35', '36-45', '46+'])
        
        age_group_stats = customer_orders.groupby('age_group')['total_amount'].agg(['mean', 'count', 'std']).round(2)
        
        print("\nSpending by Age Group:")
        for age_group, stats in age_group_stats.iterrows():
            print(f"  {age_group}: ${stats['mean']:.2f} avg (n={stats['count']})")
    
    def correlation_analysis(self):
        """
        Analyze correlations between variables.
        
        Examines relationships between:
        - Age and order value
        - Customer tenure and spending
        - Order frequency and value
        """
        print("\n" + "="*50)
        print("CORRELATION ANALYSIS")
        print("="*50)
        
        # Create customer summary for correlation analysis
        order_summary = self.orders.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count']
        }).reset_index()
        
        # Flatten column names
        order_summary.columns = ['customer_id', 'total_spent', 'avg_order_value', 'total_orders']
        
        # Merge with customers
        customer_summary = self.customers.merge(order_summary, on='customer_id', how='left')
        
        # Fill NaN values for customers with no orders
        customer_summary['total_spent'] = customer_summary['total_spent'].fillna(0)
        customer_summary['avg_order_value'] = customer_summary['avg_order_value'].fillna(0)
        customer_summary['total_orders'] = customer_summary['total_orders'].fillna(0)
        
        # Calculate days since registration
        customer_summary['days_since_registration'] = (
            pd.Timestamp.now() - customer_summary['registration_date']
        ).dt.days
        
        # Correlation 1: Age vs Total Spending
        print("\n📈 Correlation 1: Age vs Total Spending")
        spending_customers = customer_summary[customer_summary['total_spent'] > 0]
        
        if len(spending_customers) > 10:
            corr_coef, p_value = pearsonr(spending_customers['age'], spending_customers['total_spent'])
            print(f"  Correlation coefficient: {corr_coef:.3f}")
            print(f"  P-value: {p_value:.4f}")
            
            # Interpret correlation strength
            abs_corr = abs(corr_coef)
            if abs_corr < 0.1:
                strength = "negligible"
            elif abs_corr < 0.3:
                strength = "weak"
            elif abs_corr < 0.5:
                strength = "moderate"
            elif abs_corr < 0.7:
                strength = "strong"
            else:
                strength = "very strong"
            
            direction = "positive" if corr_coef > 0 else "negative"
            
            if p_value < 0.05:
                print(f"  ✅ Significant {strength} {direction} correlation")
            else:
                print(f"  ❌ No significant correlation found")
        
        # Correlation 2: Customer tenure vs spending
        print("\n📈 Correlation 2: Customer Tenure vs Total Spending")
        if len(spending_customers) > 10:
            corr_coef, p_value = pearsonr(spending_customers['days_since_registration'], 
                                        spending_customers['total_spent'])
            print(f"  Correlation coefficient: {corr_coef:.3f}")
            print(f"  P-value: {p_value:.4f}")
            
            if p_value < 0.05:
                if corr_coef > 0:
                    print("  ✅ Longer-tenured customers spend more")
                else:
                    print("  ✅ Newer customers spend more")
            else:
                print("  ❌ Customer tenure doesn't significantly affect spending")
    
    def ab_testing_simulation(self):
        """
        Simulate an A/B test for business optimization.
        
        Simulates testing a new website design that could improve conversion rates.
        """
        print("\n" + "="*50)
        print("A/B TESTING SIMULATION")
        print("="*50)
        
        print("\n🧪 Scenario: Testing New Website Design")
        print("Goal: Increase conversion rate from website visitors to customers")
        
        # Current conversion rate (from our data)
        total_customers = len(self.customers)
        customers_with_orders = len(self.orders['customer_id'].unique())
        current_conversion_rate = customers_with_orders / total_customers
        
        print(f"\nCurrent Performance:")
        print(f"  Current conversion rate: {current_conversion_rate*100:.1f}%")
        print(f"  Customers with orders: {customers_with_orders}")
        print(f"  Total customers: {total_customers}")
        
        # Simulate A/B test
        print(f"\n📊 A/B Test Setup:")
        
        # Control group (current design)
        control_visitors = 1000
        control_conversions = int(control_visitors * current_conversion_rate)
        
        # Treatment group (new design) - assume 20% improvement
        treatment_visitors = 1000
        improvement_rate = 0.20  # 20% improvement
        new_conversion_rate = current_conversion_rate * (1 + improvement_rate)
        treatment_conversions = int(treatment_visitors * new_conversion_rate)
        
        print(f"  Control group: {control_conversions} conversions from {control_visitors} visitors")
        print(f"  Treatment group: {treatment_conversions} conversions from {treatment_visitors} visitors")
        print(f"  Expected improvement: {improvement_rate*100:.0f}%")
        
        # Statistical test (Chi-square test for proportions)
        observed = [[control_conversions, control_visitors - control_conversions],
                   [treatment_conversions, treatment_visitors - treatment_conversions]]
        
        chi2, p_value, dof, expected = chi2_contingency(observed)
        
        print(f"\n📈 Statistical Results:")
        print(f"  Control conversion rate: {control_conversions/control_visitors*100:.1f}%")
        print(f"  Treatment conversion rate: {treatment_conversions/treatment_visitors*100:.1f}%")
        print(f"  Chi-square statistic: {chi2:.3f}")
        print(f"  P-value: {p_value:.4f}")
        
        if p_value < 0.05:
            print("  ✅ Statistically significant improvement!")
            print("  📊 Recommendation: Implement the new design")
        else:
            print("  ❌ No statistically significant difference")
            print("  📊 Recommendation: Need more data or larger effect")
        
        # Business impact calculation
        print(f"\n💰 Business Impact Projection:")
        monthly_visitors = 10000  # Assume 10k monthly visitors
        additional_conversions = monthly_visitors * (new_conversion_rate - current_conversion_rate)
        avg_order_value = self.orders['total_amount'].mean()
        monthly_revenue_impact = additional_conversions * avg_order_value
        annual_revenue_impact = monthly_revenue_impact * 12
        
        print(f"  Monthly additional conversions: {additional_conversions:.0f}")
        print(f"  Average order value: ${avg_order_value:.2f}")
        print(f"  Monthly revenue impact: ${monthly_revenue_impact:.2f}")
        print(f"  Annual revenue impact: ${annual_revenue_impact:.2f}")
    
    def generate_insights_summary(self):
        """
        Generate a summary of key statistical insights for business action.
        """
        print("\n" + "="*50)
        print("KEY BUSINESS INSIGHTS")
        print("="*50)
        
        # Calculate key metrics
        total_customers = len(self.customers)
        customers_with_orders = len(self.orders['customer_id'].unique())
        conversion_rate = customers_with_orders / total_customers
        avg_order_value = self.orders['total_amount'].mean()
        total_revenue = self.orders['total_amount'].sum()
        
        print(f"\n📊 Key Performance Metrics:")
        print(f"  • Customer conversion rate: {conversion_rate*100:.1f}%")
        print(f"  • Average order value: ${avg_order_value:.2f}")
        print(f"  • Total revenue: ${total_revenue:,.2f}")
        print(f"  • Revenue per customer: ${total_revenue/total_customers:.2f}")
        
        print(f"\n🎯 Strategic Recommendations:")
        
        if conversion_rate < 0.5:
            print(f"  • LOW CONVERSION ALERT: Only {conversion_rate*100:.1f}% of customers make purchases")
            print(f"    → Focus on conversion optimization")
            print(f"    → Implement welcome campaigns for new customers")
        
        # Channel analysis
        customer_orders = self.customers.merge(self.orders, on='customer_id', how='inner')
        channel_performance = customer_orders.groupby('acquisition_channel')['total_amount'].agg(['count', 'sum', 'mean'])
        best_channel = channel_performance['sum'].idxmax()
        
        print(f"  • BEST PERFORMING CHANNEL: {best_channel}")
        print(f"    → Increase marketing budget for {best_channel}")
        print(f"    → Analyze what makes {best_channel} effective")
        
        # Customer value insights
        high_value_threshold = self.orders['total_amount'].quantile(0.8)
        print(f"  • HIGH-VALUE CUSTOMERS: Orders above ${high_value_threshold:.2f}")
        print(f"    → Create VIP program for top 20% of orders")
        print(f"    → Focus retention efforts on high-value customers")
        
        print(f"\n💡 Next Steps:")
        print(f"  1. Implement A/B tests to improve conversion rates")
        print(f"  2. Develop targeted campaigns for each acquisition channel") 
        print(f"  3. Create customer segmentation strategy")
        print(f"  4. Set up retention programs for high-value customers")
    
    def run_complete_analysis(self):
        """
        Run the complete statistical analysis workflow.
        """
        print("🔍 SIMPLE STATISTICAL ANALYSIS")
        print("Analyzing customer behavior for business insights...")
        
        # Run all analyses
        self.descriptive_analysis()
        self.hypothesis_testing()
        self.correlation_analysis()
        self.ab_testing_simulation()
        self.generate_insights_summary()
        
        print(f"\n✅ Statistical analysis completed!")
        print(f"📈 Key insights generated for business decision-making")

def main():
    """
    Main function to run statistical analysis.
    """
    analyzer = SimpleStatisticalAnalyzer()
    analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()