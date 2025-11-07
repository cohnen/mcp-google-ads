# GAQL Recipe Book - Google Ads Query Language

Complete collection of GAQL queries for Performance Max campaign reporting and analysis.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Performance Max Recipes](#performance-max-recipes)
- [Budget & Pacing Recipes](#budget--pacing-recipes)
- [Asset Group Recipes](#asset-group-recipes)
- [Shopping Product Recipes](#shopping-product-recipes)
- [Campaign Comparison Recipes](#campaign-comparison-recipes)
- [Diagnostic Recipes](#diagnostic-recipes)
- [Advanced Recipes](#advanced-recipes)

---

## Quick Reference

### GAQL Basics

```sql
SELECT
  field1, field2, metrics.metric1
FROM
  resource_name
WHERE
  conditions
ORDER BY
  field DESC
LIMIT
  100
```

### Date Filtering

```sql
WHERE segments.date DURING LAST_7_DAYS
WHERE segments.date DURING LAST_30_DAYS
WHERE segments.date DURING THIS_MONTH
WHERE segments.date DURING LAST_MONTH
WHERE segments.date BETWEEN '2025-11-01' AND '2025-11-30'
WHERE segments.date = '2025-11-07'  -- Today
```

### Common Metrics

- `metrics.cost_micros` - Total spend
- `metrics.impressions` - Impressions
- `metrics.clicks` - Clicks
- `metrics.conversions` - Conversions
- `metrics.conversions_value` - Conversion value
- `metrics.all_conversions` - All conversions
- `metrics.all_conversions_value` - All conversion value

---

## Performance Max Recipes

### Recipe 1: PMax Campaign Performance (Last 7 Days)

**Use Case:** Daily dashboard, quick performance check

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.average_cpc,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.status = 'ENABLED'
  AND segments.date DURING LAST_7_DAYS
ORDER BY metrics.cost_micros DESC
LIMIT 50
```

**Expected Output:**
- Campaign performance summary
- Cost, clicks, conversions
- Sorted by spend (highest first)

**How to Use:**
```python
result = await run_gaql_query(
    account_id="1234567890",
    query="<above query>"
)
```

---

### Recipe 2: PMax Campaign Performance (Last 30 Days)

**Use Case:** Monthly reporting, trend analysis

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign_budget.amount_micros,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.conversions,
  metrics.conversions_value,
  metrics.cost_per_conversion,
  metrics.all_conversions,
  metrics.all_conversions_value
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.conversions_value DESC
LIMIT 50
```

**Calculations:**
- ROAS = conversions_value / cost_micros (both in micros)
- Budget utilization = cost_micros / (budget × 30 days)

---

### Recipe 3: PMax Daily Performance (Date Breakdown)

**Use Case:** Identify performance trends, find best/worst days

```sql
SELECT
  campaign.id,
  campaign.name,
  segments.date,
  segments.day_of_week,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.id = 9876543210
  AND segments.date DURING LAST_30_DAYS
ORDER BY segments.date DESC
```

**Analysis:**
- Day-of-week patterns
- Weekend vs weekday performance
- Spending consistency

---

### Recipe 4: PMax with Target ROAS Performance

**Use Case:** Check if campaigns are meeting ROAS targets

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.maximize_conversion_value.target_roas,
  metrics.cost_micros,
  metrics.conversions_value,
  metrics.all_conversions_value,
  metrics.conversions,
  metrics.all_conversions
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.status = 'ENABLED'
  AND campaign.maximize_conversion_value.target_roas > 0
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.cost_micros DESC
```

**Calculate Actual ROAS:**
```python
actual_roas = conversions_value / cost_micros  # Both in micros
target_roas = campaign.maximize_conversion_value.target_roas
roas_achievement = (actual_roas / target_roas) * 100  # Percentage
```

---

## Budget & Pacing Recipes

### Recipe 5: Budget Pacing Check (Today)

**Use Case:** Check if campaigns are spending correctly today

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign_budget.amount_micros,
  campaign_budget.period,
  metrics.cost_micros
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.status = 'ENABLED'
  AND segments.date = '2025-11-07'  -- Replace with TODAY
ORDER BY campaign.name
```

**Analysis:**
```python
daily_budget_micros = campaign_budget.amount_micros
actual_spend_micros = metrics.cost_micros
pacing_percentage = (actual_spend_micros / daily_budget_micros) * 100

if pacing_percentage < 50:
    status = "Under-pacing"
elif pacing_percentage > 150:
    status = "Over-pacing"
else:
    status = "On track"
```

---

### Recipe 6: Monthly Budget Utilization

**Use Case:** Month-end budget review

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign_budget.amount_micros,
  metrics.cost_micros
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.status = 'ENABLED'
  AND segments.date DURING THIS_MONTH
ORDER BY metrics.cost_micros DESC
```

**Calculate Monthly Utilization:**
```python
days_in_month = 30  # or get actual days
monthly_budget = campaign_budget.amount_micros * days_in_month
total_spend = metrics.cost_micros
utilization = (total_spend / monthly_budget) * 100
```

---

### Recipe 7: Budget Changes History

**Use Case:** Track budget adjustments over time

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign_budget.amount_micros,
  segments.date,
  metrics.cost_micros
FROM campaign
WHERE
  campaign.id = 9876543210
  AND segments.date DURING LAST_30_DAYS
ORDER BY segments.date DESC
```

**Note:** Budget changes show as the current budget for all dates. To track historical changes, you need to monitor via change history API.

---

## Asset Group Recipes

### Recipe 8: Asset Group Performance

**Use Case:** Identify best/worst performing asset groups

```sql
SELECT
  asset_group.id,
  asset_group.name,
  asset_group.status,
  campaign.name,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.conversions,
  metrics.conversions_value
FROM asset_group
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.conversions_value DESC
LIMIT 100
```

**Analysis:**
- Asset group contribution to campaign
- Identify under-performing groups
- Budget allocation insights

---

### Recipe 9: Asset Group with Final URLs

**Use Case:** Check landing pages and their performance

```sql
SELECT
  asset_group.id,
  asset_group.name,
  asset_group.final_urls,
  asset_group.status,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM asset_group
WHERE
  campaign.id = 9876543210
  AND segments.date DURING LAST_7_DAYS
ORDER BY metrics.conversions DESC
```

**URL Analysis:**
- Landing page performance
- A/B testing different URLs
- Conversion rate by destination

---

## Shopping Product Recipes

### Recipe 10: Product Performance (GMC Items)

**Use Case:** Identify best-selling products in Performance Max

```sql
SELECT
  segments.product_title,
  segments.product_item_id,
  segments.product_channel,
  segments.product_language,
  segments.product_country,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM shopping_performance_view
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.conversions_value DESC
LIMIT 100
```

**Product Insights:**
- Top revenue products
- Low-performing products to remove
- Stock planning insights

---

### Recipe 11: Product Performance by Custom Label

**Use Case:** Track products by campaign filter (feed_label)

```sql
SELECT
  segments.product_custom_attribute0,  -- This is custom_label_0 in GMC
  segments.product_title,
  metrics.cost_micros,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM shopping_performance_view
WHERE
  campaign.id = 9876543210
  AND segments.date DURING LAST_30_DAYS
  AND segments.product_custom_attribute0 = 'promo_nov2025'
ORDER BY metrics.conversions_value DESC
LIMIT 100
```

**Filter Usage:**
- Verify feed_label filtering works
- Track promotion performance
- Product set analysis

---

### Recipe 12: Out-of-Stock Products Still Showing

**Use Case:** Find products that should be paused

```sql
SELECT
  segments.product_item_id,
  segments.product_title,
  segments.product_availability,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros
FROM shopping_performance_view
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_7_DAYS
  AND segments.product_availability = 'out of stock'
  AND metrics.impressions > 0
ORDER BY metrics.cost_micros DESC
```

**Action:**
- Update GMC inventory
- Pause products via custom labels
- Check GMC sync status

---

## Campaign Comparison Recipes

### Recipe 13: Campaign Performance Comparison

**Use Case:** Compare multiple campaigns side-by-side

```sql
SELECT
  campaign.id,
  campaign.name,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.average_cpc
FROM campaign
WHERE
  campaign.id IN (111111, 222222, 333333, 444444)
  AND segments.date DURING LAST_30_DAYS
ORDER BY campaign.name
```

**Comparison Points:**
- Efficiency (CPA, ROAS)
- Scale (impressions, spend)
- Quality (CTR, conversion rate)

---

### Recipe 14: Before/After Campaign Performance

**Use Case:** Measure impact of changes (budget increase, ROAS adjustment)

```sql
SELECT
  campaign.id,
  campaign.name,
  segments.date,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE
  campaign.id = 9876543210
  AND segments.date BETWEEN '2025-10-01' AND '2025-11-30'
ORDER BY segments.date DESC
```

**Analysis:**
```python
# Compare periods
before_period = data[data.date < '2025-11-01']
after_period = data[data.date >= '2025-11-01']

before_roas = sum(before_period.conversions_value) / sum(before_period.cost_micros)
after_roas = sum(after_period.conversions_value) / sum(after_period.cost_micros)
improvement = ((after_roas - before_roas) / before_roas) * 100
```

---

## Diagnostic Recipes

### Recipe 15: Campaign Status Check

**Use Case:** Find paused or removed campaigns that should be running

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.serving_status,
  campaign.primary_status,
  campaign.primary_status_reasons
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
ORDER BY campaign.status
```

**Status Values:**
- `ENABLED` - Running
- `PAUSED` - Paused by user
- `REMOVED` - Deleted
- `UNKNOWN` - Status unknown

**Serving Status:**
- `SERVING` - Active
- `NONE` - Not serving
- `ENDED` - Campaign ended
- `PENDING` - Pending approval
- `SUSPENDED` - Suspended by Google

---

### Recipe 16: Campaign Issues and Warnings

**Use Case:** Identify campaigns with problems

```sql
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.primary_status,
  campaign.primary_status_reasons
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.primary_status != 'ELIGIBLE'
ORDER BY campaign.name
```

**Primary Status Reasons:**
- `CAMPAIGN_PAUSED` - Campaign is paused
- `CAMPAIGN_ENDED` - End date reached
- `CAMPAIGN_PENDING` - Pending approval
- `ASSET_GROUP_PAUSED` - All asset groups paused
- `BUDGET_DEPLETED` - Budget exhausted

---

### Recipe 17: Low-Performing Campaigns (Need Attention)

**Use Case:** Find campaigns that need optimization

```sql
SELECT
  campaign.id,
  campaign.name,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.impressions
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND campaign.status = 'ENABLED'
  AND segments.date DURING LAST_30_DAYS
  AND metrics.cost_micros > 100000000  -- Spent > $100
  AND metrics.conversions < 1           -- But no conversions
ORDER BY metrics.cost_micros DESC
```

**Action Items:**
- Check conversion tracking
- Review targeting/products
- Adjust ROAS targets
- Consider pausing

---

## Advanced Recipes

### Recipe 18: Hour-of-Day Performance

**Use Case:** Optimize ad scheduling

```sql
SELECT
  campaign.name,
  segments.hour,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value,
  metrics.impressions
FROM campaign
WHERE
  campaign.id = 9876543210
  AND segments.date DURING LAST_30_DAYS
ORDER BY segments.hour
```

**Analysis:**
- Best hours for conversions
- Budget allocation by hour
- Dayparting insights

---

### Recipe 19: Device Performance

**Use Case:** Understand mobile vs desktop performance

```sql
SELECT
  campaign.name,
  segments.device,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
ORDER BY campaign.name, segments.device
```

**Device Values:**
- `MOBILE` - Mobile phones
- `TABLET` - Tablets
- `DESKTOP` - Desktop computers
- `CONNECTED_TV` - Smart TVs
- `OTHER` - Other devices

---

### Recipe 20: Geographic Performance

**Use Case:** Identify best-performing locations

```sql
SELECT
  campaign.name,
  geographic_view.country_criterion_id,
  geographic_view.location_type,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM geographic_view
WHERE
  campaign.advertising_channel_type = 'PERFORMANCE_MAX'
  AND segments.date DURING LAST_30_DAYS
ORDER BY metrics.conversions_value DESC
LIMIT 100
```

**Location Analysis:**
- Top countries/regions
- Geographic expansion opportunities
- Location-specific ROAS

---

## Using Recipes with MCP Tool

All recipes can be executed using the `run_gaql_query` MCP tool:

```python
# Example: Get PMax performance for last 7 days
result = await run_gaql_query(
    account_id="1234567890",
    query="""
        SELECT
          campaign.id,
          campaign.name,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value
        FROM campaign
        WHERE
          campaign.advertising_channel_type = 'PERFORMANCE_MAX'
          AND segments.date DURING LAST_7_DAYS
        ORDER BY metrics.cost_micros DESC
    """
)
```

---

## Tips and Best Practices

### 1. Always Use Date Filters
```sql
-- Good ✅
WHERE segments.date DURING LAST_7_DAYS

-- Bad ❌ (retrieves all historical data)
WHERE campaign.status = 'ENABLED'
```

### 2. Limit Results
```sql
-- Always add LIMIT to prevent huge responses
LIMIT 100
```

### 3. Order Matters
```sql
-- Put most important sort first
ORDER BY
  metrics.conversions_value DESC,
  metrics.cost_micros DESC
```

### 4. Use Appropriate Resources
- `campaign` - Campaign-level metrics
- `asset_group` - Asset group metrics
- `shopping_performance_view` - Product metrics
- `geographic_view` - Location metrics

### 5. Metric Naming
- All monetary values end in `_micros` (divide by 1,000,000 for actual value)
- Rate metrics (CTR, conversion_rate) are already percentages

---

## Common Calculations

### ROAS (Return on Ad Spend)
```python
roas = metrics.conversions_value / metrics.cost_micros
# Both in micros, so result is already correct
# Example: 3.5 means $3.50 revenue per $1 spent
```

### CPA (Cost Per Acquisition)
```python
cpa_micros = metrics.cost_micros / metrics.conversions
cpa_currency = cpa_micros / 1_000_000
```

### Conversion Rate
```python
conversion_rate = (metrics.conversions / metrics.clicks) * 100
```

### Budget Utilization %
```python
daily_budget_micros = campaign_budget.amount_micros
spend_percentage = (metrics.cost_micros / daily_budget_micros) * 100
```

---

## Resources

- [GAQL Grammar](https://developers.google.com/google-ads/api/docs/query/grammar)
- [Google Ads API Fields](https://developers.google.com/google-ads/api/fields/v19/overview)
- [Campaign Resource](https://developers.google.com/google-ads/api/fields/v19/campaign)
- [Metrics Reference](https://developers.google.com/google-ads/api/fields/v19/metrics)
- [Segments Reference](https://developers.google.com/google-ads/api/fields/v19/segments)

---

**Happy Querying!** 🚀
