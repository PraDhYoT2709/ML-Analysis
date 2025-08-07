"""
Statistical Analysis for E-Commerce Data
========================================

This module performs comprehensive statistical analysis on e-commerce data to uncover
business insights and validate hypotheses. It demonstrates advanced statistical concepts
including hypothesis testing, probability distributions, correlation analysis, and A/B testing.

Key Statistical Concepts Covered:
- Descriptive statistics and data distribution analysis
- Hypothesis testing (t-tests, chi-square, ANOVA)
- Correlation and regression analysis
- A/B testing and statistical significance
- Customer behavior statistical modeling
- Revenue and conversion analysis
- Confidence intervals and effect sizes

Author: Data Analytics Portfolio Project
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import (
    ttest_ind, ttest_1samp, chi2_contingency, pearsonr, spearmanr,
    normaltest, levene, mannwhitneyu, kruskal, f_oneway
)
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.stats.power import ttest_power
import warnings
warnings.filterwarnings('ignore')

class EcommerceStatisticalAnalyzer:
    """
    A comprehensive class for performing statistical analysis on e-commerce data.
    
    This class provides methods for various statistical tests and analyses commonly
    used in e-commerce analytics to derive business insights and validate hypotheses.
    """
    
    def __init__(self, data_path: str = "/workspace/data/synthetic"):
        """
        Initialize the statistical analyzer with e-commerce data.
        
        Args:
            data_path (str): Path to the directory containing CSV data files
        """
        self.data_path = data_path
        self.load_data()
        self.results = {}  # Store analysis results
        
    def load_data(self):
        """
        Load all e-commerce datasets from CSV files.
        
        This method loads the synthetic data generated earlier and prepares it
        for statistical analysis by handling data types and missing values.
        """
        print("📊 Loading e-commerce data for statistical analysis...")
        
        try:
            # Load main datasets
            self.customers = pd.read_csv(f"{self.data_path}/customers.csv")
            self.products = pd.read_csv(f"{self.data_path}/products.csv")
            self.orders = pd.read_csv(f"{self.data_path}/orders.csv")
            self.order_items = pd.read_csv(f"{self.data_path}/order_items.csv")
            self.reviews = pd.read_csv(f"{self.data_path}/reviews.csv")
            self.sessions = pd.read_csv(f"{self.data_path}/website_sessions.csv")
            self.campaigns = pd.read_csv(f"{self.data_path}/marketing_campaigns.csv")
            self.segments = pd.read_csv(f"{self.data_path}/customer_segments.csv")
            
            # Convert date columns to datetime
            date_columns = {
                'customers': ['registration_date', 'last_login'],
                'orders': ['order_date', 'delivery_date'],
                'sessions': ['session_start', 'session_end']
            }
            
            for df_name, cols in date_columns.items():
                df = getattr(self, df_name)
                for col in cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            
            print("✅ Data loaded successfully")
            self.print_data_summary()
            
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("Please run the data generation script first.")
            
    def print_data_summary(self):
        """Print a summary of loaded datasets."""
        datasets = {
            'Customers': self.customers,
            'Products': self.products,
            'Orders': self.orders,
            'Order Items': self.order_items,
            'Reviews': self.reviews,
            'Sessions': self.sessions,
            'Campaigns': self.campaigns,
            'Segments': self.segments
        }
        
        print("\n📈 Dataset Summary:")
        print("-" * 40)
        for name, df in datasets.items():
            print(f"{name}: {len(df):,} records")
    
    def descriptive_statistics_analysis(self):
        """
        Perform comprehensive descriptive statistics analysis.
        
        This analysis provides foundational insights into data distributions,
        central tendencies, and variability measures that inform business decisions.
        """
        print("\n🔍 DESCRIPTIVE STATISTICS ANALYSIS")
        print("=" * 50)
        
        results = {}
        
        # 1. Customer Demographics Analysis
        print("\n👥 Customer Demographics:")
        print("-" * 30)
        
        # Age distribution (calculate from date_of_birth)
        self.customers['age'] = (pd.Timestamp.now() - pd.to_datetime(self.customers['date_of_birth'])).dt.days // 365
        
        age_stats = self.customers['age'].describe()
        print(f"Age Statistics:")
        print(f"  Mean: {age_stats['mean']:.1f} years")
        print(f"  Median: {age_stats['50%']:.1f} years")
        print(f"  Std Dev: {age_stats['std']:.1f} years")
        print(f"  Range: {age_stats['min']:.0f} - {age_stats['max']:.0f} years")
        
        # Gender distribution
        gender_dist = self.customers['gender'].value_counts(normalize=True) * 100
        print(f"\nGender Distribution:")
        for gender, pct in gender_dist.items():
            print(f"  {gender}: {pct:.1f}%")
        
        results['customer_demographics'] = {
            'age_stats': age_stats.to_dict(),
            'gender_distribution': gender_dist.to_dict()
        }
        
        # 2. Order Value Analysis
        print("\n💰 Order Value Analysis:")
        print("-" * 30)
        
        if not self.orders.empty:
            completed_orders = self.orders[self.orders['order_status'] == 'completed']
            
            if not completed_orders.empty:
                order_value_stats = completed_orders['total_amount'].describe()
                print(f"Order Value Statistics:")
                print(f"  Mean: ${order_value_stats['mean']:.2f}")
                print(f"  Median: ${order_value_stats['50%']:.2f}")
                print(f"  Std Dev: ${order_value_stats['std']:.2f}")
                print(f"  Range: ${order_value_stats['min']:.2f} - ${order_value_stats['max']:.2f}")
                
                # Calculate coefficient of variation (measure of relative variability)
                cv = (order_value_stats['std'] / order_value_stats['mean']) * 100
                print(f"  Coefficient of Variation: {cv:.1f}%")
                
                results['order_value_analysis'] = {
                    'stats': order_value_stats.to_dict(),
                    'coefficient_of_variation': cv
                }
        
        # 3. Product Performance Analysis
        print("\n📦 Product Performance Analysis:")
        print("-" * 30)
        
        # Merge order items with products to get category information
        if not self.order_items.empty and not self.products.empty:
            product_performance = self.order_items.merge(
                self.products[['product_id', 'category_name', 'unit_price']], 
                on='product_id'
            )
            
            # Sales by category
            category_sales = product_performance.groupby('category_name').agg({
                'quantity': 'sum',
                'total_price': 'sum'
            }).sort_values('total_price', ascending=False)
            
            print("Sales by Category:")
            for category, row in category_sales.iterrows():
                print(f"  {category}: {row['quantity']} units, ${row['total_price']:.2f}")
            
            results['product_performance'] = category_sales.to_dict()
        
        # 4. Session Duration Analysis
        print("\n⏱️ Website Session Analysis:")
        print("-" * 30)
        
        if not self.sessions.empty:
            session_duration_stats = self.sessions['session_duration'].describe()
            print(f"Session Duration Statistics (seconds):")
            print(f"  Mean: {session_duration_stats['mean']:.1f}")
            print(f"  Median: {session_duration_stats['50%']:.1f}")
            print(f"  Std Dev: {session_duration_stats['std']:.1f}")
            
            # Convert to minutes for better interpretation
            print(f"\nSession Duration (minutes):")
            print(f"  Mean: {session_duration_stats['mean']/60:.1f} minutes")
            print(f"  Median: {session_duration_stats['50%']/60:.1f} minutes")
            
            # Bounce rate analysis
            bounce_rate = self.sessions['bounce_rate'].mean() * 100
            print(f"\nBounce Rate: {bounce_rate:.1f}%")
            
            results['session_analysis'] = {
                'duration_stats': session_duration_stats.to_dict(),
                'bounce_rate': bounce_rate
            }
        
        self.results['descriptive_statistics'] = results
        return results
    
    def hypothesis_testing_analysis(self):
        """
        Perform various hypothesis tests to validate business assumptions.
        
        This section demonstrates different types of hypothesis tests commonly
        used in business analytics to make data-driven decisions.
        """
        print("\n🧪 HYPOTHESIS TESTING ANALYSIS")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Gender Differences in Order Values
        print("\n🔬 Test 1: Gender Differences in Order Values")
        print("-" * 45)
        print("H0: No difference in average order values between genders")
        print("H1: There is a difference in average order values between genders")
        
        if not self.orders.empty:
            # Merge orders with customer data to get gender information
            orders_with_gender = self.orders.merge(
                self.customers[['customer_id', 'gender']], 
                on='customer_id'
            )
            
            # Filter completed orders and main genders
            completed_orders_gender = orders_with_gender[
                (orders_with_gender['order_status'] == 'completed') &
                (orders_with_gender['gender'].isin(['Male', 'Female']))
            ]
            
            if len(completed_orders_gender) > 0:
                male_orders = completed_orders_gender[completed_orders_gender['gender'] == 'Male']['total_amount']
                female_orders = completed_orders_gender[completed_orders_gender['gender'] == 'Female']['total_amount']
                
                if len(male_orders) > 0 and len(female_orders) > 0:
                    # Perform independent t-test
                    t_stat, p_value = ttest_ind(male_orders, female_orders)
                    
                    print(f"Male orders - Mean: ${male_orders.mean():.2f}, N: {len(male_orders)}")
                    print(f"Female orders - Mean: ${female_orders.mean():.2f}, N: {len(female_orders)}")
                    print(f"T-statistic: {t_stat:.4f}")
                    print(f"P-value: {p_value:.4f}")
                    
                    # Interpret results
                    alpha = 0.05
                    if p_value < alpha:
                        print(f"✅ Reject H0 (p < {alpha}): Significant difference found")
                    else:
                        print(f"❌ Fail to reject H0 (p >= {alpha}): No significant difference")
                    
                    # Calculate effect size (Cohen's d)
                    pooled_std = np.sqrt(((len(male_orders)-1)*male_orders.var() + 
                                        (len(female_orders)-1)*female_orders.var()) / 
                                       (len(male_orders) + len(female_orders) - 2))
                    cohens_d = (male_orders.mean() - female_orders.mean()) / pooled_std
                    print(f"Effect size (Cohen's d): {cohens_d:.4f}")
                    
                    results['gender_order_value_test'] = {
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'cohens_d': cohens_d,
                        'male_mean': male_orders.mean(),
                        'female_mean': female_orders.mean(),
                        'significant': p_value < alpha
                    }
        
        # Test 2: Conversion Rate by Traffic Source
        print("\n🔬 Test 2: Conversion Rate Differences by Traffic Source")
        print("-" * 55)
        print("H0: No difference in conversion rates between traffic sources")
        print("H1: There are differences in conversion rates between traffic sources")
        
        if not self.sessions.empty:
            # Calculate conversion rates by traffic source
            conversion_by_source = self.sessions.groupby('traffic_source').agg({
                'conversion': ['count', 'sum']
            }).round(4)
            
            conversion_by_source.columns = ['total_sessions', 'conversions']
            conversion_by_source['conversion_rate'] = (
                conversion_by_source['conversions'] / conversion_by_source['total_sessions']
            )
            
            print("Conversion Rates by Traffic Source:")
            for source, row in conversion_by_source.iterrows():
                print(f"  {source}: {row['conversion_rate']:.4f} ({row['conversions']}/{row['total_sessions']})")
            
            # Chi-square test for independence
            # Create contingency table
            contingency_table = pd.crosstab(
                self.sessions['traffic_source'], 
                self.sessions['conversion']
            )
            
            if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                
                print(f"\nChi-square test results:")
                print(f"Chi-square statistic: {chi2:.4f}")
                print(f"P-value: {p_value:.4f}")
                print(f"Degrees of freedom: {dof}")
                
                alpha = 0.05
                if p_value < alpha:
                    print(f"✅ Reject H0 (p < {alpha}): Significant differences in conversion rates")
                else:
                    print(f"❌ Fail to reject H0 (p >= {alpha}): No significant differences")
                
                results['conversion_rate_test'] = {
                    'chi2_statistic': chi2,
                    'p_value': p_value,
                    'degrees_of_freedom': dof,
                    'conversion_rates': conversion_by_source.to_dict(),
                    'significant': p_value < alpha
                }
        
        # Test 3: Normality Test for Order Values
        print("\n🔬 Test 3: Normality Test for Order Values")
        print("-" * 40)
        print("H0: Order values follow a normal distribution")
        print("H1: Order values do not follow a normal distribution")
        
        if not self.orders.empty:
            completed_orders = self.orders[self.orders['order_status'] == 'completed']
            
            if len(completed_orders) > 0:
                order_values = completed_orders['total_amount']
                
                # D'Agostino's normality test
                stat, p_value = normaltest(order_values)
                
                print(f"D'Agostino normality test:")
                print(f"Statistic: {stat:.4f}")
                print(f"P-value: {p_value:.4f}")
                
                alpha = 0.05
                if p_value < alpha:
                    print(f"✅ Reject H0 (p < {alpha}): Order values are NOT normally distributed")
                else:
                    print(f"❌ Fail to reject H0 (p >= {alpha}): Order values may be normally distributed")
                
                # Additional descriptive statistics for distribution shape
                skewness = stats.skew(order_values)
                kurtosis = stats.kurtosis(order_values)
                
                print(f"Skewness: {skewness:.4f} ({'right-skewed' if skewness > 0 else 'left-skewed' if skewness < 0 else 'symmetric'})")
                print(f"Kurtosis: {kurtosis:.4f} ({'heavy-tailed' if kurtosis > 0 else 'light-tailed' if kurtosis < 0 else 'normal-tailed'})")
                
                results['normality_test'] = {
                    'statistic': stat,
                    'p_value': p_value,
                    'skewness': skewness,
                    'kurtosis': kurtosis,
                    'is_normal': p_value >= alpha
                }
        
        self.results['hypothesis_tests'] = results
        return results
    
    def correlation_analysis(self):
        """
        Perform correlation analysis to identify relationships between variables.
        
        This analysis helps identify which factors are related to business outcomes
        like revenue, customer satisfaction, and engagement.
        """
        print("\n📈 CORRELATION ANALYSIS")
        print("=" * 50)
        
        results = {}
        
        # 1. Customer Age vs Order Value Correlation
        print("\n🔗 Customer Age vs Order Value Correlation:")
        print("-" * 45)
        
        if not self.orders.empty:
            # Merge orders with customer data
            orders_with_age = self.orders.merge(
                self.customers[['customer_id', 'age']], 
                on='customer_id'
            )
            
            completed_orders_age = orders_with_age[orders_with_age['order_status'] == 'completed']
            
            if len(completed_orders_age) > 0:
                age_values = completed_orders_age['age']
                order_values = completed_orders_age['total_amount']
                
                # Pearson correlation (linear relationship)
                pearson_r, pearson_p = pearsonr(age_values, order_values)
                
                # Spearman correlation (monotonic relationship)
                spearman_r, spearman_p = spearmanr(age_values, order_values)
                
                print(f"Pearson correlation: r = {pearson_r:.4f}, p = {pearson_p:.4f}")
                print(f"Spearman correlation: ρ = {spearman_r:.4f}, p = {spearman_p:.4f}")
                
                # Interpret correlation strength
                def interpret_correlation(r):
                    abs_r = abs(r)
                    if abs_r < 0.1:
                        return "negligible"
                    elif abs_r < 0.3:
                        return "weak"
                    elif abs_r < 0.5:
                        return "moderate"
                    elif abs_r < 0.7:
                        return "strong"
                    else:
                        return "very strong"
                
                strength = interpret_correlation(pearson_r)
                direction = "positive" if pearson_r > 0 else "negative"
                
                print(f"Relationship: {strength} {direction} correlation")
                
                results['age_order_value_correlation'] = {
                    'pearson_r': pearson_r,
                    'pearson_p': pearson_p,
                    'spearman_r': spearman_r,
                    'spearman_p': spearman_p,
                    'strength': strength,
                    'direction': direction
                }
        
        # 2. Session Duration vs Conversion Correlation
        print("\n🔗 Session Duration vs Conversion Analysis:")
        print("-" * 45)
        
        if not self.sessions.empty:
            # Compare session durations between converted and non-converted sessions
            converted_sessions = self.sessions[self.sessions['conversion'] == True]['session_duration']
            non_converted_sessions = self.sessions[self.sessions['conversion'] == False]['session_duration']
            
            if len(converted_sessions) > 0 and len(non_converted_sessions) > 0:
                print(f"Converted sessions - Mean duration: {converted_sessions.mean():.1f} seconds")
                print(f"Non-converted sessions - Mean duration: {non_converted_sessions.mean():.1f} seconds")
                
                # Mann-Whitney U test (non-parametric alternative to t-test)
                u_stat, p_value = mannwhitneyu(converted_sessions, non_converted_sessions, alternative='two-sided')
                
                print(f"Mann-Whitney U test:")
                print(f"U-statistic: {u_stat:.4f}")
                print(f"P-value: {p_value:.4f}")
                
                alpha = 0.05
                if p_value < alpha:
                    print(f"✅ Significant difference (p < {alpha}): Session duration affects conversion")
                else:
                    print(f"❌ No significant difference (p >= {alpha}): No clear relationship")
                
                results['session_duration_conversion'] = {
                    'converted_mean_duration': converted_sessions.mean(),
                    'non_converted_mean_duration': non_converted_sessions.mean(),
                    'u_statistic': u_stat,
                    'p_value': p_value,
                    'significant': p_value < alpha
                }
        
        # 3. Product Rating vs Sales Correlation
        print("\n🔗 Product Rating vs Sales Volume Analysis:")
        print("-" * 45)
        
        if not self.reviews.empty and not self.order_items.empty:
            # Calculate average rating per product
            avg_ratings = self.reviews.groupby('product_id')['rating'].mean()
            
            # Calculate sales volume per product
            sales_volume = self.order_items.groupby('product_id')['quantity'].sum()
            
            # Merge ratings and sales data
            rating_sales_data = pd.DataFrame({
                'avg_rating': avg_ratings,
                'sales_volume': sales_volume
            }).dropna()
            
            if len(rating_sales_data) > 1:
                ratings = rating_sales_data['avg_rating']
                sales = rating_sales_data['sales_volume']
                
                # Correlation analysis
                pearson_r, pearson_p = pearsonr(ratings, sales)
                spearman_r, spearman_p = spearmanr(ratings, sales)
                
                print(f"Products analyzed: {len(rating_sales_data)}")
                print(f"Pearson correlation: r = {pearson_r:.4f}, p = {pearson_p:.4f}")
                print(f"Spearman correlation: ρ = {spearman_r:.4f}, p = {spearman_p:.4f}")
                
                strength = interpret_correlation(pearson_r)
                direction = "positive" if pearson_r > 0 else "negative"
                print(f"Relationship: {strength} {direction} correlation")
                
                results['rating_sales_correlation'] = {
                    'products_analyzed': len(rating_sales_data),
                    'pearson_r': pearson_r,
                    'pearson_p': pearson_p,
                    'spearman_r': spearman_r,
                    'spearman_p': spearman_p,
                    'strength': strength,
                    'direction': direction
                }
        
        self.results['correlation_analysis'] = results
        return results
    
    def ab_testing_simulation(self):
        """
        Simulate A/B testing scenarios for business decision making.
        
        This demonstrates how to design and analyze A/B tests, which are crucial
        for making data-driven decisions about website changes, marketing campaigns,
        and product features.
        """
        print("\n🧪 A/B TESTING SIMULATION")
        print("=" * 50)
        
        results = {}
        
        # Simulate A/B test: New website design impact on conversion rate
        print("\n🔬 A/B Test: New Website Design Impact on Conversion")
        print("-" * 55)
        print("Scenario: Testing if a new website design improves conversion rate")
        print("Control (A): Current design")
        print("Treatment (B): New design")
        
        # Simulate test data
        np.random.seed(42)  # For reproducible results
        
        # Control group (current design)
        control_visitors = 5000
        control_conversions = 250  # 5% conversion rate
        control_conversion_rate = control_conversions / control_visitors
        
        # Treatment group (new design) - assume 20% improvement
        treatment_visitors = 5000
        treatment_conversions = 300  # 6% conversion rate (20% relative improvement)
        treatment_conversion_rate = treatment_conversions / treatment_visitors
        
        print(f"\nTest Results:")
        print(f"Control Group:")
        print(f"  Visitors: {control_visitors:,}")
        print(f"  Conversions: {control_conversions:,}")
        print(f"  Conversion Rate: {control_conversion_rate:.3f} ({control_conversion_rate*100:.1f}%)")
        
        print(f"\nTreatment Group:")
        print(f"  Visitors: {treatment_visitors:,}")
        print(f"  Conversions: {treatment_conversions:,}")
        print(f"  Conversion Rate: {treatment_conversion_rate:.3f} ({treatment_conversion_rate*100:.1f}%)")
        
        # Statistical significance test using two-proportion z-test
        counts = np.array([control_conversions, treatment_conversions])
        nobs = np.array([control_visitors, treatment_visitors])
        
        z_stat, p_value = proportions_ztest(counts, nobs)
        
        print(f"\nStatistical Test Results:")
        print(f"Z-statistic: {z_stat:.4f}")
        print(f"P-value: {p_value:.4f}")
        
        alpha = 0.05
        if p_value < alpha:
            print(f"✅ Significant result (p < {alpha}): New design improves conversion rate")
        else:
            print(f"❌ Not significant (p >= {alpha}): No conclusive evidence of improvement")
        
        # Calculate confidence interval for the difference
        p1 = control_conversion_rate
        p2 = treatment_conversion_rate
        n1 = control_visitors
        n2 = treatment_visitors
        
        # Standard error for difference in proportions
        se_diff = np.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
        
        # 95% confidence interval
        diff = p2 - p1
        margin_of_error = 1.96 * se_diff  # 1.96 for 95% CI
        ci_lower = diff - margin_of_error
        ci_upper = diff + margin_of_error
        
        print(f"\nEffect Size Analysis:")
        print(f"Absolute difference: {diff:.4f} ({diff*100:.2f} percentage points)")
        print(f"Relative improvement: {(diff/p1)*100:.1f}%")
        print(f"95% Confidence Interval: [{ci_lower:.4f}, {ci_upper:.4f}]")
        
        # Power analysis
        effect_size = diff / np.sqrt(p1 * (1 - p1))  # Cohen's h for proportions
        power = ttest_power(effect_size, nobs=n1, alpha=alpha)
        
        print(f"\nPower Analysis:")
        print(f"Effect size (Cohen's h): {effect_size:.4f}")
        print(f"Statistical power: {power:.3f} ({power*100:.1f}%)")
        
        # Business impact calculation
        if p_value < alpha:
            # Assume 100,000 monthly visitors
            monthly_visitors = 100000
            additional_conversions = monthly_visitors * diff
            
            # Assume $50 average order value
            avg_order_value = 50
            monthly_revenue_impact = additional_conversions * avg_order_value
            annual_revenue_impact = monthly_revenue_impact * 12
            
            print(f"\nBusiness Impact Projection:")
            print(f"Monthly additional conversions: {additional_conversions:.0f}")
            print(f"Monthly additional revenue: ${monthly_revenue_impact:,.2f}")
            print(f"Annual additional revenue: ${annual_revenue_impact:,.2f}")
        
        results['ab_test_simulation'] = {
            'control_conversion_rate': control_conversion_rate,
            'treatment_conversion_rate': treatment_conversion_rate,
            'z_statistic': z_stat,
            'p_value': p_value,
            'significant': p_value < alpha,
            'absolute_difference': diff,
            'relative_improvement': (diff/p1)*100,
            'confidence_interval': [ci_lower, ci_upper],
            'effect_size': effect_size,
            'statistical_power': power
        }
        
        self.results['ab_testing'] = results
        return results
    
    def advanced_statistical_modeling(self):
        """
        Perform advanced statistical modeling for business insights.
        
        This section demonstrates more sophisticated statistical techniques
        that can provide deeper insights into customer behavior and business performance.
        """
        print("\n📊 ADVANCED STATISTICAL MODELING")
        print("=" * 50)
        
        results = {}
        
        # 1. Customer Lifetime Value Statistical Distribution
        print("\n💰 Customer Lifetime Value Distribution Analysis:")
        print("-" * 55)
        
        if not self.segments.empty:
            clv_values = self.segments['clv_prediction'].dropna()
            
            if len(clv_values) > 0:
                # Descriptive statistics
                clv_stats = clv_values.describe()
                print(f"CLV Statistics:")
                print(f"  Mean: ${clv_stats['mean']:.2f}")
                print(f"  Median: ${clv_stats['50%']:.2f}")
                print(f"  Std Dev: ${clv_stats['std']:.2f}")
                print(f"  Skewness: {stats.skew(clv_values):.3f}")
                print(f"  Kurtosis: {stats.kurtosis(clv_values):.3f}")
                
                # Test for different distributions
                distributions = ['norm', 'lognorm', 'gamma', 'expon']
                best_dist = None
                best_p = 0
                
                print(f"\nDistribution Fitting (Kolmogorov-Smirnov test):")
                for dist_name in distributions:
                    dist = getattr(stats, dist_name)
                    params = dist.fit(clv_values)
                    ks_stat, p_value = stats.kstest(clv_values, lambda x: dist.cdf(x, *params))
                    
                    print(f"  {dist_name.capitalize()}: KS = {ks_stat:.4f}, p = {p_value:.4f}")
                    
                    if p_value > best_p:
                        best_p = p_value
                        best_dist = dist_name
                
                print(f"\nBest fitting distribution: {best_dist.capitalize()} (p = {best_p:.4f})")
                
                results['clv_distribution'] = {
                    'statistics': clv_stats.to_dict(),
                    'skewness': stats.skew(clv_values),
                    'kurtosis': stats.kurtosis(clv_values),
                    'best_distribution': best_dist,
                    'best_p_value': best_p
                }
        
        # 2. Churn Probability Analysis
        print("\n⚠️ Churn Probability Statistical Analysis:")
        print("-" * 45)
        
        if not self.segments.empty:
            churn_probs = self.segments['churn_probability'].dropna()
            
            if len(churn_probs) > 0:
                # Analyze churn probability distribution
                print(f"Churn Probability Statistics:")
                print(f"  Mean: {churn_probs.mean():.3f}")
                print(f"  Median: {churn_probs.median():.3f}")
                print(f"  Std Dev: {churn_probs.std():.3f}")
                
                # Risk categories
                low_risk = (churn_probs <= 0.3).sum()
                medium_risk = ((churn_probs > 0.3) & (churn_probs <= 0.7)).sum()
                high_risk = (churn_probs > 0.7).sum()
                
                total_customers = len(churn_probs)
                
                print(f"\nChurn Risk Categories:")
                print(f"  Low Risk (≤30%): {low_risk} customers ({low_risk/total_customers*100:.1f}%)")
                print(f"  Medium Risk (31-70%): {medium_risk} customers ({medium_risk/total_customers*100:.1f}%)")
                print(f"  High Risk (>70%): {high_risk} customers ({high_risk/total_customers*100:.1f}%)")
                
                results['churn_analysis'] = {
                    'mean_churn_prob': churn_probs.mean(),
                    'median_churn_prob': churn_probs.median(),
                    'std_churn_prob': churn_probs.std(),
                    'risk_categories': {
                        'low_risk': {'count': low_risk, 'percentage': low_risk/total_customers*100},
                        'medium_risk': {'count': medium_risk, 'percentage': medium_risk/total_customers*100},
                        'high_risk': {'count': high_risk, 'percentage': high_risk/total_customers*100}
                    }
                }
        
        self.results['advanced_modeling'] = results
        return results
    
    def generate_statistical_report(self):
        """
        Generate a comprehensive statistical analysis report.
        
        This method compiles all analysis results into a structured report
        that can be used for business decision making and presentation.
        """
        print("\n📋 GENERATING STATISTICAL ANALYSIS REPORT")
        print("=" * 50)
        
        # Run all analyses
        self.descriptive_statistics_analysis()
        self.hypothesis_testing_analysis()
        self.correlation_analysis()
        self.ab_testing_simulation()
        self.advanced_statistical_modeling()
        
        # Generate summary report
        report = {
            'analysis_date': pd.Timestamp.now().isoformat(),
            'data_summary': {
                'customers': len(self.customers),
                'orders': len(self.orders),
                'products': len(self.products),
                'sessions': len(self.sessions)
            },
            'key_findings': [],
            'recommendations': [],
            'statistical_results': self.results
        }
        
        # Extract key findings
        if 'descriptive_statistics' in self.results:
            desc_stats = self.results['descriptive_statistics']
            if 'customer_demographics' in desc_stats:
                avg_age = desc_stats['customer_demographics']['age_stats']['mean']
                report['key_findings'].append(f"Average customer age is {avg_age:.1f} years")
        
        if 'hypothesis_tests' in self.results:
            hyp_tests = self.results['hypothesis_tests']
            if 'gender_order_value_test' in hyp_tests:
                if hyp_tests['gender_order_value_test']['significant']:
                    report['key_findings'].append("Significant gender differences in order values detected")
                else:
                    report['key_findings'].append("No significant gender differences in order values")
        
        if 'ab_testing' in self.results:
            ab_results = self.results['ab_testing']['ab_test_simulation']
            if ab_results['significant']:
                improvement = ab_results['relative_improvement']
                report['key_findings'].append(f"A/B test shows {improvement:.1f}% relative improvement in conversion rate")
        
        # Generate recommendations
        report['recommendations'] = [
            "Continue monitoring customer demographics for targeting strategies",
            "Implement A/B testing framework for website optimizations",
            "Focus retention efforts on high-churn-probability customers",
            "Leverage correlation insights for cross-selling opportunities",
            "Use statistical significance testing for all business decisions"
        ]
        
        # Save report
        import json
        report_path = "/workspace/reports/statistical_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Statistical analysis report saved to: {report_path}")
        
        # Print executive summary
        print(f"\n📊 EXECUTIVE SUMMARY")
        print("-" * 30)
        print(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Datasets Analyzed: {len(report['data_summary'])} datasets")
        print(f"Key Findings: {len(report['key_findings'])} insights")
        print(f"Recommendations: {len(report['recommendations'])} action items")
        
        print(f"\n🔍 Key Findings:")
        for i, finding in enumerate(report['key_findings'], 1):
            print(f"  {i}. {finding}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        return report

def main():
    """
    Main function to run the complete statistical analysis.
    """
    print("=" * 60)
    print("📊 E-COMMERCE STATISTICAL ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = EcommerceStatisticalAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_statistical_report()
    
    print("\n🎉 Statistical analysis completed successfully!")
    print("📋 Report saved and ready for business decision making.")

if __name__ == "__main__":
    main()