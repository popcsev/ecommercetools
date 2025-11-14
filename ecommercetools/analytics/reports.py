"""
Pre-built GA4 report templates for multi-country e-commerce setups.

IMPORTANT: This module is designed for setups where each GA4 property
represents a different country/region website (e.g., yoursite.co.uk,
yoursite.de, yoursite.com).

The 'country_label' comes from which property you're querying, NOT from
the visitor's physical location. For example:
- UK property (yoursite.co.uk) → country_label = 'UK'
- All visitors to that property are counted as 'UK', regardless of where
  they're physically located.

Do NOT use GA4's 'country' dimension, as that tracks visitor location,
not which website/property they're on.
"""

import pandas as pd
from typing import Optional, List
from ecommercetools.analytics.ga4 import query_ga4_multi_country


def get_daily_traffic_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get daily traffic metrics for all properties.

    Returns sessions, users, pageviews, and engagement metrics by date
    for each property (country).

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with columns: country_label, date, sessions, totalUsers,
        newUsers, screenPageViews, averageSessionDuration, bounceRate

    Example:
        >>> df = get_daily_traffic_report(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> # Aggregate by country
        >>> summary = df.groupby('country_label').agg({
        ...     'sessions': 'sum',
        ...     'totalUsers': 'sum'
        ... })
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['date'],
        metrics=[
            'sessions',
            'totalUsers',
            'newUsers',
            'screenPageViews',
            'averageSessionDuration',
            'bounceRate'
        ],
        countries=countries
    )


def get_source_medium_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get traffic by source and medium (acquisition channels).

    Shows where your traffic is coming from (Google, Facebook, Direct, etc.)
    for each property.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with columns: country_label, sessionSource, sessionMedium,
        sessions, totalUsers, conversions, engagementRate

    Example:
        >>> df = get_source_medium_report(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> # Top sources by country
        >>> top_sources = df.groupby(['country_label', 'sessionSource'])['sessions'].sum()
        >>> print(top_sources.nlargest(20))
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['sessionSource', 'sessionMedium'],
        metrics=[
            'sessions',
            'totalUsers',
            'newUsers',
            'conversions',
            'engagementRate'
        ],
        countries=countries
    )


def get_landing_pages_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """Get landing page performance for each property.

    Shows which pages users land on and their performance metrics.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include
        limit: Max rows per property (default: 10000)

    Returns:
        DataFrame with columns: country_label, landingPage, sessions,
        totalUsers, bounceRate, conversions

    Example:
        >>> df = get_landing_pages_report(
        ...     'service_account.json',
        ...     'ga4_properties.json',
        ...     countries=['US', 'UK']
        ... )
        >>> # Top landing pages per country
        >>> for country in ['US', 'UK']:
        ...     top = df[df['country_label'] == country].nlargest(10, 'sessions')
        ...     print(f"\\n{country} Top Pages:")
        ...     print(top[['landingPage', 'sessions']])
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['landingPage'],
        metrics=[
            'sessions',
            'totalUsers',
            'bounceRate',
            'conversions',
            'engagementRate'
        ],
        countries=countries,
        limit=limit
    )


def get_device_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get traffic breakdown by device category (desktop/mobile/tablet).

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with columns: country_label, deviceCategory, sessions,
        totalUsers, conversions, engagementRate

    Example:
        >>> df = get_device_report(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> # Mobile vs Desktop by country
        >>> pivot = df.pivot_table(
        ...     values='sessions',
        ...     index='country_label',
        ...     columns='deviceCategory',
        ...     aggfunc='sum'
        ... )
        >>> print(pivot)
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['deviceCategory'],
        metrics=[
            'sessions',
            'totalUsers',
            'conversions',
            'engagementRate'
        ],
        countries=countries
    )


def get_ecommerce_overview_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get e-commerce overview by date for each property.

    Daily e-commerce metrics including transactions, revenue, and conversion rates.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with columns: country_label, date, transactions, totalRevenue,
        averagePurchaseRevenue, ecommercePurchases, itemsViewed, addToCarts

    Example:
        >>> df = get_ecommerce_overview_report(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> # Total revenue by country
        >>> revenue = df.groupby('country_label')['totalRevenue'].sum().sort_values(ascending=False)
        >>> print(revenue)
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['date'],
        metrics=[
            'transactions',
            'totalRevenue',
            'averagePurchaseRevenue',
            'ecommercePurchases',
            'itemsViewed',
            'addToCarts'
        ],
        countries=countries
    )


def get_product_performance_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """Get product-level performance metrics for each property.

    Shows how individual products are performing across different properties.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include
        limit: Max rows per property (default: 10000)

    Returns:
        DataFrame with columns: country_label, itemName, itemBrand, itemCategory,
        itemRevenue, itemsViewed, itemsPurchased, itemsAddedToCart

    Example:
        >>> df = get_product_performance_report(
        ...     'service_account.json',
        ...     'ga4_properties.json',
        ...     countries=['US', 'UK', 'DE']
        ... )
        >>> # Best selling products by country
        >>> for country in ['US', 'UK', 'DE']:
        ...     top = df[df['country_label'] == country].nlargest(10, 'itemRevenue')
        ...     print(f"\\n{country} Top Products:")
        ...     print(top[['itemName', 'itemRevenue', 'itemsPurchased']])
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['itemName', 'itemBrand', 'itemCategory'],
        metrics=[
            'itemRevenue',
            'itemsViewed',
            'itemsPurchased',
            'itemsAddedToCart',
            'cartToViewRate',
            'purchaseToViewRate'
        ],
        countries=countries,
        limit=limit
    )


def get_conversion_funnel_report(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get conversion funnel metrics by source/medium.

    Shows how different traffic sources convert through your funnel.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with columns: country_label, sessionSource, sessionMedium,
        sessions, engagedSessions, conversions, transactions, totalRevenue

    Example:
        >>> df = get_conversion_funnel_report(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> # Calculate conversion rates
        >>> df['conversion_rate'] = (df['conversions'] / df['sessions'] * 100).round(2)
        >>> df['transaction_rate'] = (df['transactions'] / df['sessions'] * 100).round(2)
        >>> print(df.nlargest(20, 'conversions'))
    """
    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=['sessionSource', 'sessionMedium'],
        metrics=[
            'sessions',
            'engagedSessions',
            'conversions',
            'transactions',
            'totalRevenue',
            'engagementRate'
        ],
        countries=countries
    )


def create_multi_country_summary(
    credentials_path: str,
    config_path: str,
    start_date: str = '30daysAgo',
    end_date: str = 'yesterday',
    countries: Optional[List[str]] = None
) -> pd.DataFrame:
    """Create a high-level summary comparing all properties.

    Provides a single-row summary for each property with key metrics.

    Args:
        credentials_path: Path to service account JSON
        config_path: Path to property config JSON
        start_date: Start date (default: 30daysAgo)
        end_date: End date (default: yesterday)
        countries: Optional list of countries to include

    Returns:
        DataFrame with one row per property showing: country_label, sessions,
        users, revenue, transactions, conversion_rate, avg_order_value, etc.

    Example:
        >>> summary = create_multi_country_summary(
        ...     'service_account.json',
        ...     'ga4_properties.json'
        ... )
        >>> print(summary.sort_values('totalRevenue', ascending=False))
    """
    df = query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=[],  # No dimensions = property-level aggregation
        metrics=[
            'sessions',
            'totalUsers',
            'newUsers',
            'screenPageViews',
            'averageSessionDuration',
            'bounceRate',
            'engagementRate',
            'conversions',
            'transactions',
            'totalRevenue',
            'averagePurchaseRevenue'
        ],
        countries=countries
    )

    # Calculate additional metrics
    if not df.empty:
        df['conversion_rate'] = (df['conversions'] / df['sessions'] * 100).round(2)
        df['transaction_rate'] = (df['transactions'] / df['sessions'] * 100).round(2)
        df['pages_per_session'] = (df['screenPageViews'] / df['sessions']).round(2)
        df['new_user_rate'] = (df['newUsers'] / df['totalUsers'] * 100).round(2)

    return df
