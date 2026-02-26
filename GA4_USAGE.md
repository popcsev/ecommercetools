# Google Analytics 4 (GA4) Multi-Country Setup Guide

This guide shows how to use the new **Analytics** module to query GA4 data across multiple countries using a centralized configuration file.

## Table of Contents
- [Setup](#setup)
- [Configuration File](#configuration-file)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Pre-built Reports](#pre-built-reports)
- [Available Dimensions & Metrics](#available-dimensions--metrics)

---

## Setup

### 1. Install Dependencies

The analytics module requires the Google Analytics Data API client:

```bash
pip install google-analytics-data>=0.16.0
```

### 2. Create Service Account Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the "Google Analytics Data API"
4. Create a Service Account
5. Download the JSON credentials file
6. Grant the service account "Viewer" access to each GA4 property

### 3. Create Property Configuration File

Create a JSON file mapping country codes to GA4 property IDs:

**`ga4_properties.json`:**
```json
{
  "US": "properties/123456789",
  "UK": "properties/987654321",
  "DE": "properties/111222333",
  "FR": "properties/444555666",
  "ES": "properties/777888999"
}
```

---

## Configuration File

The configuration file structure is simple:

```json
{
  "COUNTRY_CODE": "properties/PROPERTY_ID",
  "ANOTHER_COUNTRY": "properties/ANOTHER_ID"
}
```

- **Keys**: Country codes or labels (your choice - can be "US", "United States", "USA", etc.)
- **Values**: GA4 property IDs in the format `properties/XXXXXXXXX`

The country label (key) will be added as a `country_label` column in your results.

---

## Basic Usage

### Query a Single Property

```python
from ecommercetools import analytics

# Query US property for last 30 days
df = analytics.query_ga4(
    credentials_path='service_account.json',
    property_id='properties/123456789',
    start_date='30daysAgo',
    end_date='today',
    dimensions=['date', 'city'],
    metrics=['sessions', 'totalUsers', 'transactions']
)

print(df.head())
```

### Query Multiple Countries

```python
from ecommercetools import analytics

# Query all countries in config file
df = analytics.query_ga4_multi_country(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='2024-01-01',
    end_date='2024-01-31',
    dimensions=['date', 'sessionSource'],
    metrics=['sessions', 'totalUsers', 'transactions']
)

# Results include 'country_label' column automatically
print(df.head())
```

**Output:**
```
  country_label        date sessionSource  sessions  totalUsers  transactions
0            US  2024-01-01        google      1234         980            45
1            US  2024-01-01      facebook       567         432            12
2            UK  2024-01-01        google       890         701            32
...
```

### Query Specific Countries Only

```python
# Query only US, UK, and DE
df = analytics.query_ga4_multi_country(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='7daysAgo',
    end_date='today',
    dimensions=['date'],
    metrics=['sessions', 'conversions'],
    countries=['US', 'UK', 'DE']  # Only these countries
)
```

---

## Advanced Usage

### Custom Dimensions and Metrics

```python
from ecommercetools import analytics

# E-commerce focused query
df = analytics.query_ga4_multi_country(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='2024-01-01',
    end_date='2024-01-31',
    dimensions=['date', 'itemName', 'itemCategory'],
    metrics=[
        'itemRevenue',
        'itemsViewed',
        'itemsPurchased',
        'itemsAddedToCart',
        'cartToViewRate',
        'purchaseToViewRate'
    ],
    countries=['US', 'UK', 'FR', 'DE']
)

# Analyze by country
summary = df.groupby('country_label').agg({
    'itemRevenue': 'sum',
    'itemsPurchased': 'sum',
    'itemsViewed': 'sum'
}).reset_index()

print(summary)
```

### Without Country Label

If you want to query multiple properties but don't need the country label:

```python
df = analytics.query_ga4_multi_country(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='yesterday',
    end_date='today',
    dimensions=['sessionSource', 'sessionMedium'],
    metrics=['sessions'],
    add_country_label=False  # Don't add country_label column
)
```

---

## Pre-built Reports

The module includes pre-configured reports for common use cases:

### 1. Traffic Report

Daily traffic metrics:

```python
from ecommercetools import analytics

traffic_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='today',
    report_type='traffic'
)

# Includes: sessions, totalUsers, newUsers, screenPageViews,
#           averageSessionDuration, bounceRate
```

### 2. Acquisition Report

User acquisition by source/medium:

```python
acquisition_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='2024-01-01',
    end_date='2024-01-31',
    report_type='acquisition',
    countries=['US', 'UK']  # Optional: specific countries
)

# Includes: sessions, totalUsers, newUsers, conversions, engagementRate
# Dimensions: sessionSource, sessionMedium, sessionCampaignName
```

### 3. E-commerce Report

```python
ecommerce_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='7daysAgo',
    end_date='today',
    report_type='ecommerce'
)

# Includes: itemRevenue, itemsViewed, itemsPurchased, itemsAddedToCart,
#           transactions, totalRevenue
# Dimensions: date, itemName
```

### 4. Pages Report

```python
pages_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='yesterday',
    end_date='today',
    report_type='pages'
)

# Includes: screenPageViews, totalUsers, averageSessionDuration, bounceRate
# Dimensions: pageTitle, pagePath
```

### 5. Devices Report

```python
devices_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='today',
    report_type='devices'
)

# Includes: sessions, totalUsers, conversions, engagementRate
# Dimensions: deviceCategory, operatingSystem
```

---

## Available Dimensions & Metrics

### Common Dimensions

**Traffic:**
- `date`
- `year`, `month`, `day`
- `dateHour`
- `dayOfWeek`

**User:**
- `country`
- `city`
- `region`
- `newVsReturning`
- `userAgeBracket`
- `userGender`

**Session:**
- `sessionSource`
- `sessionMedium`
- `sessionCampaignName`
- `deviceCategory`
- `operatingSystem`
- `browser`

**Page:**
- `pageTitle`
- `pagePath`
- `pagePathPlusQueryString`
- `landingPage`
- `exitPage`

**E-commerce:**
- `itemName`
- `itemBrand`
- `itemCategory`
- `transactionId`

### Common Metrics

**Users & Sessions:**
- `totalUsers`
- `newUsers`
- `activeUsers`
- `sessions`
- `sessionsPerUser`
- `screenPageViews`
- `screenPageViewsPerSession`

**Engagement:**
- `averageSessionDuration`
- `bounceRate`
- `engagementRate`
- `engagedSessions`
- `userEngagementDuration`

**E-commerce:**
- `transactions`
- `totalRevenue`
- `purchaseRevenue`
- `itemRevenue`
- `itemsViewed`
- `itemsPurchased`
- `itemsAddedToCart`
- `cartToViewRate`
- `purchaseToViewRate`

**Conversions:**
- `conversions`
- `eventCount`
- `eventCountPerUser`

For the complete list, see [GA4 Dimensions & Metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).

---

## Complete Example: Multi-Country Analysis

```python
from ecommercetools import analytics
import pandas as pd

# 1. Load configuration
config = analytics.load_property_config('ga4_properties.json')
print(f"Configured countries: {list(config.keys())}")

# 2. Get traffic data for all countries
traffic_df = analytics.get_ga4_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday',
    report_type='traffic'
)

# 3. Analyze by country
country_summary = traffic_df.groupby('country_label').agg({
    'sessions': 'sum',
    'totalUsers': 'sum',
    'newUsers': 'sum',
    'screenPageViews': 'sum'
}).reset_index()

country_summary['pages_per_session'] = (
    country_summary['screenPageViews'] / country_summary['sessions']
).round(2)

print("\n=== Country Summary ===")
print(country_summary.sort_values('sessions', ascending=False))

# 4. Get e-commerce data
ecommerce_df = analytics.query_ga4_multi_country(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday',
    dimensions=['itemName', 'itemCategory'],
    metrics=['itemRevenue', 'itemsPurchased', 'itemsViewed'],
    countries=['US', 'UK', 'DE']  # Top 3 markets
)

# 5. Top products by country
for country in ['US', 'UK', 'DE']:
    top_products = (
        ecommerce_df[ecommerce_df['country_label'] == country]
        .nlargest(10, 'itemRevenue')
    )
    print(f"\n=== Top 10 Products: {country} ===")
    print(top_products[['itemName', 'itemRevenue', 'itemsPurchased']])

# 6. Export to CSV
traffic_df.to_csv('ga4_traffic_multi_country.csv', index=False)
ecommerce_df.to_csv('ga4_ecommerce_multi_country.csv', index=False)
```

---

## Error Handling

```python
from ecommercetools import analytics

try:
    df = analytics.query_ga4_multi_country(
        credentials_path='service_account.json',
        config_path='ga4_properties.json',
        start_date='7daysAgo',
        end_date='today',
        dimensions=['date'],
        metrics=['sessions'],
        countries=['US', 'INVALID']  # INVALID not in config
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Query error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Tips & Best Practices

1. **Date Formats**: Use relative dates (`'30daysAgo'`, `'yesterday'`, `'today'`) or absolute dates (`'2024-01-01'`)

2. **Rate Limits**: GA4 API has limits. For large datasets:
   - Increase the `limit` parameter (default: 10,000)
   - Query smaller date ranges
   - Use pagination if needed

3. **Service Account Permissions**: Ensure your service account has "Viewer" role on all properties

4. **Country Labels**: Use consistent naming in your JSON config (ISO codes recommended: US, UK, DE, etc.)

5. **Caching**: Consider caching results for expensive queries:
   ```python
   df = analytics.query_ga4_multi_country(...)
   df.to_parquet('cache_30days.parquet')  # Cache results
   ```

6. **Testing**: Start with a single country before querying all:
   ```python
   # Test first
   test_df = analytics.query_ga4_multi_country(
       ...,
       countries=['US'],  # Just one country
       limit=100  # Small limit
   )
   ```

---

## Next Steps

- Add more countries to your `ga4_properties.json` config
- Create custom reports for your specific use cases
- Combine GA4 data with other ecommercetools modules (customers, products, transactions)
- Schedule automated reports using cron or Airflow

For more information, see the [ecommercetools repository](https://github.com/popcsev/ecommercetools).
