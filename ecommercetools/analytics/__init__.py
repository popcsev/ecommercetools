"""
Analytics module for Google Analytics 4 (GA4) data retrieval and analysis.

IMPORTANT FOR MULTI-COUNTRY SETUPS:
This module is designed for setups where each GA4 property represents a
different country/region website (e.g., yoursite.co.uk, yoursite.de).

The 'country_label' comes from which property you're querying (defined in
your JSON config), NOT from the visitor's physical location.

Example: UK property → all visitors labeled as 'UK', regardless of where
they're physically located.
"""

from ecommercetools.analytics.ga4 import (
    load_property_config,
    query_ga4,
    query_ga4_multi_country,
    get_ga4_report
)

from ecommercetools.analytics.reports import (
    get_daily_traffic_report,
    get_source_medium_report,
    get_landing_pages_report,
    get_device_report,
    get_ecommerce_overview_report,
    get_product_performance_report,
    get_conversion_funnel_report,
    create_multi_country_summary
)

__all__ = [
    # Core functions
    'load_property_config',
    'query_ga4',
    'query_ga4_multi_country',
    'get_ga4_report',
    # Pre-built reports
    'get_daily_traffic_report',
    'get_source_medium_report',
    'get_landing_pages_report',
    'get_device_report',
    'get_ecommerce_overview_report',
    'get_product_performance_report',
    'get_conversion_funnel_report',
    'create_multi_country_summary'
]
