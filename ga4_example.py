"""
Example usage of the GA4 Analytics module for multi-country setups.

Before running this script:
1. Create a service account in Google Cloud Console
2. Download the credentials JSON file
3. Grant the service account "Viewer" access to your GA4 properties
4. Create a ga4_properties.json config file with your property mappings
"""

from ecommercetools import analytics
import pandas as pd

# Configure paths
CREDENTIALS_PATH = 'service_account.json'  # Your service account credentials
CONFIG_PATH = 'ga4_properties.json'        # Your property configuration

# Example 1: Load and view configuration
print("=" * 60)
print("Example 1: Load Property Configuration")
print("=" * 60)

try:
    config = analytics.load_property_config(CONFIG_PATH)
    print(f"\nConfigured countries: {list(config.keys())}")
    for country, property_id in config.items():
        print(f"  {country}: {property_id}")
except FileNotFoundError:
    print(f"\nConfiguration file not found: {CONFIG_PATH}")
    print("Please create ga4_properties.json with your property IDs.")
    print("\nExample format:")
    print('{')
    print('  "US": "properties/123456789",')
    print('  "UK": "properties/987654321"')
    print('}')
    exit(1)

# Example 2: Get traffic report for all countries
print("\n" + "=" * 60)
print("Example 2: Traffic Report (Last 7 Days)")
print("=" * 60)

try:
    traffic_df = analytics.get_ga4_report(
        credentials_path=CREDENTIALS_PATH,
        config_path=CONFIG_PATH,
        start_date='7daysAgo',
        end_date='yesterday',
        report_type='traffic'
    )

    print(f"\nRetrieved {len(traffic_df)} rows")
    print("\nSample data:")
    print(traffic_df.head(10))

    # Country summary
    summary = traffic_df.groupby('country_label').agg({
        'sessions': 'sum',
        'totalUsers': 'sum',
        'screenPageViews': 'sum'
    }).reset_index()

    print("\n=== Summary by Country ===")
    print(summary.sort_values('sessions', ascending=False))

except Exception as e:
    print(f"\nError: {e}")
    print("\nMake sure:")
    print("1. Service account credentials are valid")
    print("2. Service account has access to all GA4 properties")
    print("3. Property IDs in config are correct")

# Example 3: Get acquisition data for specific countries
print("\n" + "=" * 60)
print("Example 3: Acquisition Report (Specific Countries)")
print("=" * 60)

try:
    # Query only US and UK
    acquisition_df = analytics.get_ga4_report(
        credentials_path=CREDENTIALS_PATH,
        config_path=CONFIG_PATH,
        start_date='30daysAgo',
        end_date='yesterday',
        report_type='acquisition',
        countries=['US', 'UK']  # Only these countries
    )

    print(f"\nRetrieved {len(acquisition_df)} rows")
    print("\nTop sources by country:")
    print(acquisition_df.groupby(['country_label', 'sessionSource'])['sessions'].sum().nlargest(10))

except ValueError as e:
    print(f"\nConfiguration error: {e}")
except Exception as e:
    print(f"\nError: {e}")

# Example 4: Custom query with specific dimensions and metrics
print("\n" + "=" * 60)
print("Example 4: Custom Query")
print("=" * 60)

try:
    custom_df = analytics.query_ga4_multi_country(
        credentials_path=CREDENTIALS_PATH,
        config_path=CONFIG_PATH,
        start_date='yesterday',
        end_date='yesterday',
        dimensions=['deviceCategory', 'country'],
        metrics=['sessions', 'conversions', 'engagementRate'],
        limit=100
    )

    print(f"\nRetrieved {len(custom_df)} rows")
    print("\nDevice breakdown by country:")
    pivot = custom_df.pivot_table(
        values='sessions',
        index='deviceCategory',
        columns='country_label',
        aggfunc='sum',
        fill_value=0
    )
    print(pivot)

except Exception as e:
    print(f"\nError: {e}")

# Example 5: E-commerce data
print("\n" + "=" * 60)
print("Example 5: E-commerce Report")
print("=" * 60)

try:
    ecommerce_df = analytics.get_ga4_report(
        credentials_path=CREDENTIALS_PATH,
        config_path=CONFIG_PATH,
        start_date='7daysAgo',
        end_date='yesterday',
        report_type='ecommerce'
    )

    print(f"\nRetrieved {len(ecommerce_df)} rows")

    # Top products by revenue
    top_products = (
        ecommerce_df.groupby('itemName')['itemRevenue']
        .sum()
        .nlargest(10)
        .reset_index()
    )

    print("\n=== Top 10 Products by Revenue ===")
    print(top_products)

    # Revenue by country
    country_revenue = (
        ecommerce_df.groupby('country_label')['totalRevenue']
        .sum()
        .reset_index()
        .sort_values('totalRevenue', ascending=False)
    )

    print("\n=== Revenue by Country ===")
    print(country_revenue)

except Exception as e:
    print(f"\nError: {e}")

print("\n" + "=" * 60)
print("Examples complete!")
print("=" * 60)
print("\nFor more information, see GA4_USAGE.md")
