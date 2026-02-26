"""
Google Analytics 4 (GA4) data retrieval and analysis functions.

This module provides functions to query GA4 properties across multiple countries
using a configuration file that maps country names to GA4 property IDs.
"""

import json
import pandas as pd
from typing import Dict, List, Optional, Union
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account


def load_property_config(config_path: str) -> Dict[str, str]:
    """Load GA4 property configuration from JSON file.

    The JSON file should have the structure:
    {
        "US": "properties/123456789",
        "UK": "properties/987654321",
        "DE": "properties/111222333"
    }

    Args:
        config_path (str): Path to the JSON configuration file containing
                          country-to-property-ID mappings.

    Returns:
        dict: Dictionary mapping country names to GA4 property IDs.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        json.JSONDecodeError: If config file is not valid JSON.

    Example:
        >>> config = load_property_config('ga4_properties.json')
        >>> print(config['US'])
        'properties/123456789'
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")


def _create_client(credentials_path: str) -> BetaAnalyticsDataClient:
    """Create and return a GA4 API client.

    Args:
        credentials_path (str): Path to Google service account JSON credentials.

    Returns:
        BetaAnalyticsDataClient: Authenticated GA4 client.

    Raises:
        RuntimeError: If client creation fails.
    """
    try:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=credentials)
        return client
    except Exception as e:
        raise RuntimeError(f"Failed to create GA4 client: {e}")


def query_ga4(
    credentials_path: str,
    property_id: str,
    start_date: str,
    end_date: str,
    dimensions: List[str],
    metrics: List[str],
    limit: int = 10000
) -> pd.DataFrame:
    """Query a single GA4 property and return results as a DataFrame.

    Args:
        credentials_path (str): Path to Google service account JSON credentials.
        property_id (str): GA4 property ID (e.g., 'properties/123456789').
        start_date (str): Start date in YYYY-MM-DD format or 'yesterday', '7daysAgo', etc.
        end_date (str): End date in YYYY-MM-DD format or 'today', 'yesterday', etc.
        dimensions (list): List of dimension names (e.g., ['country', 'city', 'date']).
        metrics (list): List of metric names (e.g., ['sessions', 'totalUsers', 'transactions']).
        limit (int, optional): Maximum number of rows to return. Defaults to 10000.

    Returns:
        pd.DataFrame: DataFrame containing the query results.

    Raises:
        RuntimeError: If the query fails.

    Example:
        >>> df = query_ga4(
        ...     credentials_path='service_account.json',
        ...     property_id='properties/123456789',
        ...     start_date='2024-01-01',
        ...     end_date='2024-01-31',
        ...     dimensions=['date', 'country'],
        ...     metrics=['sessions', 'totalUsers']
        ... )
    """
    try:
        client = _create_client(credentials_path)

        # Build request
        request = RunReportRequest(
            property=property_id,
            dimensions=[Dimension(name=dim) for dim in dimensions],
            metrics=[Metric(name=metric) for metric in metrics],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            limit=limit
        )

        # Execute request
        response = client.run_report(request)

        # Parse response into DataFrame
        rows_data = []
        for row in response.rows:
            row_dict = {}

            # Add dimensions
            for i, dimension_value in enumerate(row.dimension_values):
                row_dict[dimensions[i]] = dimension_value.value

            # Add metrics
            for i, metric_value in enumerate(row.metric_values):
                row_dict[metrics[i]] = metric_value.value

            rows_data.append(row_dict)

        df = pd.DataFrame(rows_data)

        # Convert metric columns to numeric
        for metric in metrics:
            if metric in df.columns:
                df[metric] = pd.to_numeric(df[metric], errors='coerce')

        return df

    except Exception as e:
        raise RuntimeError(f"GA4 query failed for property {property_id}: {e}")


def query_ga4_multi_country(
    credentials_path: str,
    config_path: str,
    start_date: str,
    end_date: str,
    dimensions: List[str],
    metrics: List[str],
    countries: Optional[List[str]] = None,
    limit: int = 10000,
    add_country_label: bool = True
) -> pd.DataFrame:
    """Query multiple GA4 properties (one per country) and combine results.

    This function loads country-to-property mappings from a JSON config file,
    queries each property, and combines the results into a single DataFrame
    with country labels.

    Args:
        credentials_path (str): Path to Google service account JSON credentials.
        config_path (str): Path to JSON file mapping countries to property IDs.
        start_date (str): Start date in YYYY-MM-DD format or relative (e.g., '7daysAgo').
        end_date (str): End date in YYYY-MM-DD format or relative (e.g., 'today').
        dimensions (list): List of dimension names.
        metrics (list): List of metric names.
        countries (list, optional): List of countries to query. If None, queries all
                                   countries in config. Defaults to None.
        limit (int, optional): Maximum rows per property. Defaults to 10000.
        add_country_label (bool, optional): Add 'country_label' column from config keys.
                                           Defaults to True.

    Returns:
        pd.DataFrame: Combined DataFrame with data from all queried properties.

    Raises:
        RuntimeError: If any query fails.

    Example:
        >>> # Query US, UK, and DE properties
        >>> df = query_ga4_multi_country(
        ...     credentials_path='service_account.json',
        ...     config_path='ga4_properties.json',
        ...     start_date='2024-01-01',
        ...     end_date='2024-01-31',
        ...     dimensions=['date', 'sessionSource'],
        ...     metrics=['sessions', 'transactions'],
        ...     countries=['US', 'UK', 'DE']
        ... )
        >>> print(df.head())
    """
    # Load property configuration
    property_config = load_property_config(config_path)

    # Determine which countries to query
    if countries is None:
        countries = list(property_config.keys())
    else:
        # Validate requested countries exist in config
        missing = set(countries) - set(property_config.keys())
        if missing:
            raise ValueError(f"Countries not found in config: {missing}")

    # Query each property and collect results
    all_data = []

    for country in countries:
        property_id = property_config[country]

        try:
            df = query_ga4(
                credentials_path=credentials_path,
                property_id=property_id,
                start_date=start_date,
                end_date=end_date,
                dimensions=dimensions,
                metrics=metrics,
                limit=limit
            )

            # Add country label column
            if add_country_label:
                df['country_label'] = country

            all_data.append(df)

        except Exception as e:
            raise RuntimeError(f"Failed to query {country} (property: {property_id}): {e}")

    # Combine all dataframes
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)

        # Reorder columns to put country_label first if it exists
        if add_country_label and 'country_label' in combined_df.columns:
            cols = ['country_label'] + [col for col in combined_df.columns if col != 'country_label']
            combined_df = combined_df[cols]

        return combined_df
    else:
        return pd.DataFrame()


def get_ga4_report(
    credentials_path: str,
    config_path: str,
    start_date: str,
    end_date: str,
    report_type: str = 'traffic',
    countries: Optional[List[str]] = None,
    limit: int = 10000
) -> pd.DataFrame:
    """Get a pre-configured GA4 report for common use cases.

    This is a convenience function that provides pre-defined dimension and metric
    combinations for common reporting scenarios.

    Args:
        credentials_path (str): Path to Google service account JSON credentials.
        config_path (str): Path to JSON file mapping countries to property IDs.
        start_date (str): Start date in YYYY-MM-DD format or relative.
        end_date (str): End date in YYYY-MM-DD format or relative.
        report_type (str): Type of report. Options:
            - 'traffic': Basic traffic metrics by date
            - 'acquisition': User acquisition by source/medium
            - 'ecommerce': E-commerce performance metrics
            - 'pages': Page performance metrics
            - 'devices': Traffic by device category
        countries (list, optional): Countries to include. Defaults to all in config.
        limit (int, optional): Maximum rows per property. Defaults to 10000.

    Returns:
        pd.DataFrame: Report data.

    Raises:
        ValueError: If report_type is not recognized.

    Example:
        >>> # Get traffic report for all countries
        >>> traffic_df = get_ga4_report(
        ...     credentials_path='service_account.json',
        ...     config_path='ga4_properties.json',
        ...     start_date='30daysAgo',
        ...     end_date='today',
        ...     report_type='traffic'
        ... )

        >>> # Get e-commerce report for US only
        >>> ecommerce_df = get_ga4_report(
        ...     credentials_path='service_account.json',
        ...     config_path='ga4_properties.json',
        ...     start_date='2024-01-01',
        ...     end_date='2024-01-31',
        ...     report_type='ecommerce',
        ...     countries=['US']
        ... )
    """
    # Define report configurations
    report_configs = {
        'traffic': {
            'dimensions': ['date'],
            'metrics': ['sessions', 'totalUsers', 'newUsers', 'screenPageViews', 'averageSessionDuration', 'bounceRate']
        },
        'acquisition': {
            'dimensions': ['sessionSource', 'sessionMedium', 'sessionCampaignName'],
            'metrics': ['sessions', 'totalUsers', 'newUsers', 'conversions', 'engagementRate']
        },
        'ecommerce': {
            'dimensions': ['date', 'itemName'],
            'metrics': ['itemRevenue', 'itemsViewed', 'itemsPurchased', 'itemsAddedToCart', 'transactions', 'totalRevenue']
        },
        'pages': {
            'dimensions': ['pageTitle', 'pagePath'],
            'metrics': ['screenPageViews', 'totalUsers', 'averageSessionDuration', 'bounceRate']
        },
        'devices': {
            'dimensions': ['deviceCategory', 'operatingSystem'],
            'metrics': ['sessions', 'totalUsers', 'conversions', 'engagementRate']
        }
    }

    if report_type not in report_configs:
        raise ValueError(
            f"Unknown report_type: '{report_type}'. "
            f"Available types: {', '.join(report_configs.keys())}"
        )

    config = report_configs[report_type]

    return query_ga4_multi_country(
        credentials_path=credentials_path,
        config_path=config_path,
        start_date=start_date,
        end_date=end_date,
        dimensions=config['dimensions'],
        metrics=config['metrics'],
        countries=countries,
        limit=limit,
        add_country_label=True
    )
