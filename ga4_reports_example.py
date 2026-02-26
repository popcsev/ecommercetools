"""
Example: Using GA4 Analytics Reports for Multi-Country E-commerce

This script demonstrates how to use the pre-built GA4 reports for a
multi-country setup where each GA4 property represents a different
country website.

SETUP:
- Each property = one country's website (e.g., yoursite.co.uk, yoursite.de)
- The country_label comes from which property you're querying, NOT from
  the visitor's location
- All visitors to UK property are labeled 'UK' regardless of where they're
  physically located
"""

from ecommercetools import analytics
import pandas as pd

# Configure your files
CREDENTIALS = 'service_account.json'
CONFIG = 'ga4_properties.json'

# Set pandas display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)


def example_1_multi_country_summary():
    """Get a high-level summary comparing all properties."""
    print("=" * 80)
    print("EXAMPLE 1: Multi-Country Summary (Last 30 Days)")
    print("=" * 80)

    summary = analytics.create_multi_country_summary(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday'
    )

    print("\nKey Metrics by Country/Property:")
    print(summary.sort_values('totalRevenue', ascending=False))

    # Show top performers
    print("\n--- TOP 5 BY REVENUE ---")
    top_revenue = summary.nlargest(5, 'totalRevenue')[['country_label', 'totalRevenue', 'transactions']]
    print(top_revenue)

    print("\n--- TOP 5 BY SESSIONS ---")
    top_sessions = summary.nlargest(5, 'sessions')[['country_label', 'sessions', 'totalUsers']]
    print(top_sessions)

    return summary


def example_2_daily_traffic():
    """Get daily traffic trends for all properties."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Daily Traffic Report (Last 7 Days)")
    print("=" * 80)

    traffic = analytics.get_daily_traffic_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='7daysAgo',
        end_date='yesterday'
    )

    print(f"\nTotal rows: {len(traffic)}")
    print("\nSample data:")
    print(traffic.head(14))

    # Aggregate by country
    by_country = traffic.groupby('country_label').agg({
        'sessions': 'sum',
        'totalUsers': 'sum',
        'screenPageViews': 'sum'
    }).reset_index()

    by_country['pages_per_session'] = (
        by_country['screenPageViews'] / by_country['sessions']
    ).round(2)

    print("\n--- TRAFFIC BY COUNTRY ---")
    print(by_country.sort_values('sessions', ascending=False))

    return traffic


def example_3_acquisition_sources():
    """Analyze traffic sources for each property."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Traffic Sources by Property (Last 30 Days)")
    print("=" * 80)

    sources = analytics.get_source_medium_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday'
    )

    # Top sources overall
    print("\n--- TOP 10 TRAFFIC SOURCES (ALL PROPERTIES) ---")
    top_sources = (
        sources.groupby(['sessionSource', 'sessionMedium'])['sessions']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top_sources)

    # Top sources by country
    print("\n--- TOP 5 SOURCES PER COUNTRY ---")
    for country in sources['country_label'].unique()[:3]:  # First 3 countries
        country_data = sources[sources['country_label'] == country]
        top = country_data.nlargest(5, 'sessions')[['sessionSource', 'sessionMedium', 'sessions']]
        print(f"\n{country}:")
        print(top)

    return sources


def example_4_ecommerce_performance():
    """Analyze e-commerce performance across properties."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: E-commerce Overview (Last 30 Days)")
    print("=" * 80)

    ecommerce = analytics.get_ecommerce_overview_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday'
    )

    # Total revenue by country
    revenue_by_country = (
        ecommerce.groupby('country_label')
        .agg({
            'transactions': 'sum',
            'totalRevenue': 'sum',
            'averagePurchaseRevenue': 'mean'
        })
        .reset_index()
        .sort_values('totalRevenue', ascending=False)
    )

    print("\n--- REVENUE BY COUNTRY ---")
    print(revenue_by_country)

    # Daily trends for top country
    if not revenue_by_country.empty:
        top_country = revenue_by_country.iloc[0]['country_label']
        daily_trend = ecommerce[ecommerce['country_label'] == top_country][
            ['date', 'transactions', 'totalRevenue']
        ].sort_values('date')

        print(f"\n--- DAILY TREND: {top_country} (Last 7 Days) ---")
        print(daily_trend.tail(7))

    return ecommerce


def example_5_product_performance():
    """Analyze product performance across countries."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Product Performance (Last 30 Days)")
    print("=" * 80)

    # Query specific countries only
    products = analytics.get_product_performance_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday',
        countries=['US', 'UK', 'DE'],  # Top 3 markets only
        limit=1000
    )

    print(f"\nTotal product records: {len(products)}")

    # Top products by revenue across all queried countries
    print("\n--- TOP 10 PRODUCTS BY REVENUE (US + UK + DE) ---")
    top_products = (
        products.groupby('itemName')['itemRevenue']
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(top_products)

    # Best sellers per country
    print("\n--- BEST SELLERS BY COUNTRY ---")
    for country in ['US', 'UK', 'DE']:
        country_products = products[products['country_label'] == country]
        if not country_products.empty:
            top = country_products.nlargest(5, 'itemRevenue')[
                ['itemName', 'itemRevenue', 'itemsPurchased']
            ]
            print(f"\n{country}:")
            print(top)

    return products


def example_6_device_breakdown():
    """Analyze device usage across properties."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Device Breakdown (Last 30 Days)")
    print("=" * 80)

    devices = analytics.get_device_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday'
    )

    # Pivot table: countries vs devices
    pivot = devices.pivot_table(
        values='sessions',
        index='country_label',
        columns='deviceCategory',
        aggfunc='sum',
        fill_value=0
    )

    print("\n--- SESSIONS BY DEVICE & COUNTRY ---")
    print(pivot)

    # Calculate percentages
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
    print("\n--- PERCENTAGE BY DEVICE & COUNTRY ---")
    print(pivot_pct.round(1))

    return devices


def example_7_conversion_funnel():
    """Analyze conversion rates by traffic source."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Conversion Funnel by Source (Last 30 Days)")
    print("=" * 80)

    funnel = analytics.get_conversion_funnel_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday'
    )

    # Calculate conversion rates
    funnel['conversion_rate'] = (funnel['conversions'] / funnel['sessions'] * 100).round(2)
    funnel['transaction_rate'] = (funnel['transactions'] / funnel['sessions'] * 100).round(2)

    # Top converting sources
    print("\n--- TOP 10 SOURCES BY CONVERSIONS ---")
    top_converting = funnel.nlargest(10, 'conversions')[
        ['country_label', 'sessionSource', 'sessionMedium', 'sessions', 'conversions', 'conversion_rate']
    ]
    print(top_converting)

    # Best conversion rates (min 100 sessions)
    print("\n--- BEST CONVERSION RATES (Min 100 sessions) ---")
    best_rates = funnel[funnel['sessions'] >= 100].nlargest(10, 'conversion_rate')[
        ['country_label', 'sessionSource', 'sessionMedium', 'sessions', 'conversion_rate']
    ]
    print(best_rates)

    return funnel


def example_8_landing_pages():
    """Analyze landing page performance."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Top Landing Pages (Last 30 Days)")
    print("=" * 80)

    pages = analytics.get_landing_pages_report(
        credentials_path=CREDENTIALS,
        config_path=CONFIG,
        start_date='30daysAgo',
        end_date='yesterday',
        limit=500
    )

    # Top pages by sessions
    print("\n--- TOP 20 LANDING PAGES BY SESSIONS ---")
    top_pages = pages.nlargest(20, 'sessions')[
        ['country_label', 'landingPage', 'sessions', 'bounceRate', 'conversions']
    ]
    print(top_pages)

    return pages


def example_9_export_reports():
    """Export all reports to CSV files."""
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Export Reports to CSV")
    print("=" * 80)

    # Summary
    summary = analytics.create_multi_country_summary(CREDENTIALS, CONFIG)
    summary.to_csv('ga4_summary.csv', index=False)
    print("✓ Exported: ga4_summary.csv")

    # Traffic
    traffic = analytics.get_daily_traffic_report(CREDENTIALS, CONFIG)
    traffic.to_csv('ga4_daily_traffic.csv', index=False)
    print("✓ Exported: ga4_daily_traffic.csv")

    # Sources
    sources = analytics.get_source_medium_report(CREDENTIALS, CONFIG)
    sources.to_csv('ga4_sources.csv', index=False)
    print("✓ Exported: ga4_sources.csv")

    # E-commerce
    ecommerce = analytics.get_ecommerce_overview_report(CREDENTIALS, CONFIG)
    ecommerce.to_csv('ga4_ecommerce.csv', index=False)
    print("✓ Exported: ga4_ecommerce.csv")

    print("\nAll reports exported successfully!")


# Main execution
if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("GA4 ANALYTICS REPORTS - MULTI-COUNTRY SETUP")
    print("=" * 80)
    print("\nNOTE: Each property represents a different country website.")
    print("The country_label shows which property/website, NOT visitor location.\n")

    try:
        # Run examples
        example_1_multi_country_summary()
        example_2_daily_traffic()
        example_3_acquisition_sources()
        example_4_ecommerce_performance()
        example_5_product_performance()
        example_6_device_breakdown()
        example_7_conversion_funnel()
        example_8_landing_pages()
        example_9_export_reports()

        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("1. service_account.json - Google service account credentials")
        print("2. ga4_properties.json - Property configuration file")
        print("\nSee GA4_USAGE.md for setup instructions.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCheck that:")
        print("1. Service account has access to all GA4 properties")
        print("2. Property IDs in config file are correct")
        print("3. Date ranges are valid")
