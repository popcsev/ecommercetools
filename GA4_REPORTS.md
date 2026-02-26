# GA4 Analytics Reports - Multi-Country Setup

This guide shows how to use pre-built GA4 reports for **multi-country e-commerce setups** where each GA4 property represents a different country's website.

## Important: Understanding Your Setup

**Your Multi-Country Architecture:**
```
├── yoursite.com (US)     → GA4 Property: properties/123456789
├── yoursite.co.uk (UK)   → GA4 Property: properties/987654321
├── yoursite.de (DE)      → GA4 Property: properties/111222333
└── yoursite.fr (FR)      → GA4 Property: properties/444555666
```

**Key Concept:**
- Each **property** = one country's **website**
- The `country_label` comes from **which property** you're querying (defined in your JSON config)
- **NOT** from the visitor's physical location

**Example:**
- A visitor from India browsing yoursite.co.uk → labeled as **'UK'**
- A visitor from France browsing yoursite.co.uk → labeled as **'UK'**
- All visitors to the UK property are **'UK'**, regardless of their location

**Do NOT use GA4's `country` dimension** - that tracks visitor location, not which website they're on!

---

## Quick Start

### 1. Create Configuration File

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

### 2. Use Pre-built Reports

```python
from ecommercetools import analytics

# Get high-level summary for all properties
summary = analytics.create_multi_country_summary(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

print(summary)
```

**Output:**
```
  country_label  sessions  totalUsers  transactions  totalRevenue  conversion_rate
0            US     45230       38901          1234      125000.50             2.73
1            UK     32145       27823           892       89500.25             2.78
2            DE     28901       24567           756       72300.00             2.62
3            FR     21234       18456           543       54200.75             2.56
4            ES     18923       16234           478       48900.30             2.53
```

---

## Available Reports

### 1. Multi-Country Summary

**One-row summary per property/country** with all key metrics.

```python
summary = analytics.create_multi_country_summary(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Includes calculated metrics:
# - conversion_rate
# - transaction_rate
# - pages_per_session
# - new_user_rate
```

**Use Case:** Executive dashboard, country comparison

---

### 2. Daily Traffic Report

**Daily traffic metrics** for each property.

```python
traffic = analytics.get_daily_traffic_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Metrics included:
# - sessions, totalUsers, newUsers
# - screenPageViews
# - averageSessionDuration
# - bounceRate
```

**Example - Traffic Trends:**
```python
import matplotlib.pyplot as plt

# Plot sessions over time for each country
for country in ['US', 'UK', 'DE']:
    data = traffic[traffic['country_label'] == country]
    plt.plot(data['date'], data['sessions'], label=country)

plt.legend()
plt.title('Sessions by Country')
plt.show()
```

---

### 3. Source/Medium Report

**Traffic acquisition by source** (Google, Facebook, Direct, etc.) for each property.

```python
sources = analytics.get_source_medium_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Top sources by country
for country in ['US', 'UK', 'DE']:
    top = sources[sources['country_label'] == country].nlargest(5, 'sessions')
    print(f"\n{country} Top Sources:")
    print(top[['sessionSource', 'sessionMedium', 'sessions']])
```

**Use Case:** Channel performance analysis, marketing attribution

---

### 4. E-commerce Overview

**Daily e-commerce metrics** for each property.

```python
ecommerce = analytics.get_ecommerce_overview_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Revenue by country
revenue = ecommerce.groupby('country_label')['totalRevenue'].sum()
print(revenue.sort_values(ascending=False))
```

**Metrics:**
- transactions, totalRevenue
- averagePurchaseRevenue
- ecommercePurchases
- itemsViewed, addToCarts

---

### 5. Product Performance

**Product-level performance** across properties.

```python
products = analytics.get_product_performance_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday',
    countries=['US', 'UK', 'DE'],  # Specific countries only
    limit=1000
)

# Best sellers by country
for country in ['US', 'UK', 'DE']:
    top = products[products['country_label'] == country].nlargest(10, 'itemRevenue')
    print(f"\n{country} Best Sellers:")
    print(top[['itemName', 'itemRevenue', 'itemsPurchased']])
```

**Use Case:** Product merchandising, inventory planning by market

---

### 6. Landing Pages Report

**Landing page performance** for each property.

```python
pages = analytics.get_landing_pages_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Top landing pages by country
for country in ['US', 'UK']:
    top = pages[pages['country_label'] == country].nlargest(10, 'sessions')
    print(f"\n{country} Top Landing Pages:")
    print(top[['landingPage', 'sessions', 'bounceRate']])
```

**Use Case:** SEO analysis, content optimization

---

### 7. Device Breakdown

**Desktop vs Mobile vs Tablet** for each property.

```python
devices = analytics.get_device_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Pivot table
pivot = devices.pivot_table(
    values='sessions',
    index='country_label',
    columns='deviceCategory',
    aggfunc='sum'
)

print(pivot)
```

**Output:**
```
deviceCategory    desktop   mobile  tablet
country_label
DE                  15234    12456    1211
FR                  11234     9234     766
UK                  18234    12345    1566
US                  25234    18456    1540
```

---

### 8. Conversion Funnel

**Conversion rates by traffic source** for each property.

```python
funnel = analytics.get_conversion_funnel_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

# Calculate rates
funnel['conversion_rate'] = (funnel['conversions'] / funnel['sessions'] * 100).round(2)

# Best converting sources
best = funnel[funnel['sessions'] >= 100].nlargest(20, 'conversion_rate')
print(best)
```

**Use Case:** Marketing optimization, budget allocation

---

## Complete Example Workflow

```python
from ecommercetools import analytics
import pandas as pd

# 1. High-level overview
print("=" * 60)
print("MULTI-COUNTRY PERFORMANCE OVERVIEW")
print("=" * 60)

summary = analytics.create_multi_country_summary(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

print("\nTop Countries by Revenue:")
print(summary.nlargest(5, 'totalRevenue')[
    ['country_label', 'sessions', 'transactions', 'totalRevenue', 'conversion_rate']
])

# 2. Traffic trends
print("\n" + "=" * 60)
print("TRAFFIC TRENDS (Last 7 Days)")
print("=" * 60)

traffic = analytics.get_daily_traffic_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='7daysAgo',
    end_date='yesterday'
)

# Aggregate by country
by_country = traffic.groupby('country_label').agg({
    'sessions': 'sum',
    'totalUsers': 'sum'
}).sort_values('sessions', ascending=False)

print(by_country)

# 3. E-commerce deep dive for top 3 countries
print("\n" + "=" * 60)
print("E-COMMERCE PERFORMANCE (Top 3 Countries)")
print("=" * 60)

top_3 = summary.nlargest(3, 'totalRevenue')['country_label'].tolist()

products = analytics.get_product_performance_report(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday',
    countries=top_3
)

for country in top_3:
    print(f"\n{country} - Best Sellers:")
    top_products = products[products['country_label'] == country].nlargest(5, 'itemRevenue')
    print(top_products[['itemName', 'itemRevenue', 'itemsPurchased']])

# 4. Export for further analysis
traffic.to_csv('ga4_traffic_30days.csv', index=False)
summary.to_csv('ga4_summary.csv', index=False)
products.to_csv('ga4_products.csv', index=False)

print("\n✓ Reports exported to CSV files")
```

---

## Common Analysis Patterns

### Compare Countries

```python
summary = analytics.create_multi_country_summary(...)

# Revenue comparison
print(summary.sort_values('totalRevenue', ascending=False))

# Conversion rate comparison
print(summary.sort_values('conversion_rate', ascending=False))

# Visualize
import matplotlib.pyplot as plt

summary.plot(
    x='country_label',
    y=['sessions', 'totalRevenue'],
    kind='bar',
    subplots=True,
    figsize=(12, 8)
)
plt.tight_layout()
plt.show()
```

### Analyze Seasonality

```python
traffic = analytics.get_daily_traffic_report(
    start_date='90daysAgo',
    end_date='yesterday',
    ...
)

# Add day of week
traffic['day_of_week'] = pd.to_datetime(traffic['date']).dt.day_name()

# Average by day of week
weekly_pattern = traffic.groupby(['country_label', 'day_of_week'])['sessions'].mean()
print(weekly_pattern)
```

### Identify Growth Opportunities

```python
sources = analytics.get_source_medium_report(...)

# Countries with low Google organic traffic
organic = sources[sources['sessionSource'] == 'google']
organic = sources[sources['sessionMedium'] == 'organic']

organic_by_country = organic.groupby('country_label')['sessions'].sum()
print("\nOrganic Traffic by Country:")
print(organic_by_country.sort_values(ascending=True))
# Low organic = SEO opportunity
```

---

## Scheduling Reports

### Daily Report Email

```python
import schedule
import time
from datetime import datetime
from ecommercetools import analytics

def send_daily_report():
    """Run daily at 9 AM"""
    summary = analytics.create_multi_country_summary(
        credentials_path='service_account.json',
        config_path='ga4_properties.json',
        start_date='yesterday',
        end_date='yesterday'
    )

    # Email or save
    summary.to_csv(f'reports/daily_{datetime.now():%Y%m%d}.csv', index=False)
    print(f"Daily report generated: {datetime.now()}")

schedule.every().day.at("09:00").do(send_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## Tips for Multi-Country Analysis

1. **Always use country_label** for grouping, not GA4's 'country' dimension
2. **Start with summary** to identify top/bottom performers
3. **Focus on top 3-5 countries** for detailed analysis
4. **Compare conversion rates** not just absolute numbers
5. **Look for patterns** - which sources work in which countries?
6. **Export regularly** for historical trending

---

## Troubleshooting

**"Countries not found in config"**
- Check your JSON file has the correct country codes
- Make sure you're using the same codes in both config and function calls

**"Failed to query {country}"**
- Check service account has access to that property
- Verify property ID is correct in config file

**Missing data for some countries**
- Some properties may have no data for the date range
- Check GA4 property is receiving data

---

For more information, see:
- **GA4_USAGE.md** - Full API documentation
- **ga4_reports_example.py** - Runnable examples
- **ga4_example.py** - Basic usage
