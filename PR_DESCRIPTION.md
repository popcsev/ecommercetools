# Add GA4 Analytics Module for Multi-Country E-commerce

## Summary

This PR adds a complete **GA4 Analytics module** designed specifically for multi-country e-commerce setups where each GA4 property represents a different country's website (e.g., yoursite.co.uk, yoursite.de, yoursite.com).

## Key Features

### 🆕 New Analytics Module
- **Location:** `ecommercetools/analytics/`
- Query multiple GA4 properties in a single call
- Automatic country labeling from JSON configuration
- Support for all GA4 dimensions and metrics
- Pre-built reports for common use cases

### 📊 8 Pre-built Reports
1. `create_multi_country_summary()` - High-level overview
2. `get_daily_traffic_report()` - Daily traffic metrics
3. `get_source_medium_report()` - Traffic acquisition
4. `get_landing_pages_report()` - Landing page performance
5. `get_device_report()` - Device breakdown
6. `get_ecommerce_overview_report()` - E-commerce metrics
7. `get_product_performance_report()` - Product-level data
8. `get_conversion_funnel_report()` - Conversion analysis

### 🌍 Multi-Country Architecture
- Each property = one country website
- `country_label` from JSON config (not visitor location)
- Query all countries or specific subset
- Automatic data aggregation

## Usage Example

```python
from ecommercetools import analytics

# Get summary for all countries
summary = analytics.create_multi_country_summary(
    credentials_path='service_account.json',
    config_path='ga4_properties.json',
    start_date='30daysAgo',
    end_date='yesterday'
)

print(summary.sort_values('totalRevenue', ascending=False))
```

**Configuration** (`ga4_properties.json`):
```json
{
  "US": "properties/123456789",
  "UK": "properties/987654321",
  "DE": "properties/111222333"
}
```

## Files Changed

### New Files
- `ecommercetools/analytics/__init__.py` - Module exports
- `ecommercetools/analytics/ga4.py` - Core GA4 functions
- `ecommercetools/analytics/reports.py` - Pre-built reports
- `GA4_USAGE.md` - Comprehensive usage guide
- `GA4_REPORTS.md` - Multi-country reports guide
- `ga4_example.py` - Basic examples
- `ga4_reports_example.py` - Complete examples (9 use cases)
- `ga4_properties_example.json` - Configuration template

### Modified Files
- `requirements.txt` - Added `google-analytics-data>=0.16.0`, removed `gapandas`
- `setup.py` - Added GA4 dependency, updated metadata for fork
- `README.md` - Added Analytics section, updated installation
- `.gitignore` - Added GA4 config files
- `ecommercetools/__init__.py` - Removed author attribution

## Dependencies

**Added:**
- `google-analytics-data>=0.16.0` (official GA4 API client)

**Removed:**
- `gapandas` (outdated, replaced by modern GA4 API)

## Documentation

Complete documentation provided:
- **GA4_USAGE.md** - API reference, dimensions/metrics, examples
- **GA4_REPORTS.md** - Multi-country setup guide, analysis patterns
- **Example scripts** - 9 runnable examples

## Breaking Changes

None. This is purely additive - all existing functionality remains unchanged.

## Testing

Manual testing required:
1. Install from fork: `pip install git+https://github.com/popcsev/ecommercetools.git`
2. Create service account credentials
3. Create `ga4_properties.json` config
4. Run example scripts

## Installation

**From GitHub (recommended):**
```bash
pip install git+https://github.com/popcsev/ecommercetools.git
```

**Local development:**
```bash
git clone https://github.com/popcsev/ecommercetools.git
cd ecommercetools
pip install -e .
```

## Commits Included

1. `af09e9f` - Add GA4 Analytics module with multi-country support
2. `2348165` - Remove outdated gapandas dependency
3. `5325cc2` - Add pre-built GA4 reports for multi-country e-commerce setups
4. `18dfb5f` - Update documentation and metadata for fork

## Related

This PR builds on the previously merged critical fixes (#2) and adds the GA4 functionality as a new feature module.

---

**Ready for review and merge! 🚀**
