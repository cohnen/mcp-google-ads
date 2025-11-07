# ✅ Phase 6 Complete - GAQL Recipe Book & Query Tool

## 🚀 Phase 6 Summary

Phase 6 adds **comprehensive GAQL query recipes** and a tool to execute them!

### สิ่งที่ทำเสร็จ:

1. ✅ **GAQL Recipe Book** (`docs/GAQL_RECIPES.md`)
   - 20 ready-to-use query recipes
   - Complete examples for all common use cases
   - Best practices and tips

2. ✅ **run_gaql_query Tool**
   - Execute custom GAQL queries
   - Support for pagination
   - Comprehensive error handling

3. ✅ **Query Categories**
   - Performance Max campaign reporting
   - Budget and pacing analysis
   - Asset group performance
   - Shopping product analytics
   - Campaign comparisons
   - Diagnostic queries

---

## 📦 New Files & Updates

### Files Created:
```
docs/GAQL_RECIPES.md            # 800+ lines - Query recipe book
PHASE6_COMPLETE.md              # This file
```

### Files Updated:
```
google_ads_server.py            # Added run_gaql_query tool
```

---

## 🎯 GAQL Recipes Included

### Performance Max Recipes (4 recipes)
1. **PMax Campaign Performance (Last 7 Days)** - Daily dashboard
2. **PMax Campaign Performance (Last 30 Days)** - Monthly reporting
3. **PMax Daily Performance** - Date breakdown with trends
4. **PMax with Target ROAS Performance** - ROAS achievement tracking

### Budget & Pacing Recipes (3 recipes)
5. **Budget Pacing Check (Today)** - Real-time pacing monitoring
6. **Monthly Budget Utilization** - Month-end budget review
7. **Budget Changes History** - Track budget adjustments

### Asset Group Recipes (2 recipes)
8. **Asset Group Performance** - Best/worst performing groups
9. **Asset Group with Final URLs** - Landing page analysis

### Shopping Product Recipes (3 recipes)
10. **Product Performance (GMC Items)** - Best-selling products
11. **Product Performance by Custom Label** - Track by feed_label
12. **Out-of-Stock Products Still Showing** - Inventory issues

### Campaign Comparison Recipes (2 recipes)
13. **Campaign Performance Comparison** - Side-by-side comparison
14. **Before/After Campaign Performance** - Measure impact of changes

### Diagnostic Recipes (3 recipes)
15. **Campaign Status Check** - Find paused campaigns
16. **Campaign Issues and Warnings** - Identify problems
17. **Low-Performing Campaigns** - Need optimization

### Advanced Recipes (3 recipes)
18. **Hour-of-Day Performance** - Ad scheduling optimization
19. **Device Performance** - Mobile vs desktop
20. **Geographic Performance** - Location analysis

---

## 🔧 Using the run_gaql_query Tool

### Basic Usage

```python
result = await run_gaql_query(
    account_id="1234567890",
    query="SELECT campaign.id, campaign.name, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_7_DAYS"
)
```

### Response Format

```json
{
  "success": true,
  "account_id": "1234567890",
  "result_count": 5,
  "results": [
    {
      "campaign": {
        "id": "9876543210",
        "name": "SEW | Sunglasses PMax | TH | 2025-11"
      },
      "metrics": {
        "costMicros": "1500000000"
      }
    }
  ],
  "field_mask": "campaign.id,campaign.name,metrics.cost_micros",
  "total_results_count": 5,
  "next_page_token": null
}
```

---

## 📊 Example Use Cases

### Use Case 1: Daily Performance Dashboard

**Scenario:** Check yesterday's performance for all PMax campaigns

```python
result = await run_gaql_query(
    account_id="1234567890",
    query="""
        SELECT
          campaign.id,
          campaign.name,
          metrics.cost_micros,
          metrics.conversions,
          metrics.conversions_value,
          metrics.impressions,
          metrics.clicks
        FROM campaign
        WHERE
          campaign.advertising_channel_type = 'PERFORMANCE_MAX'
          AND campaign.status = 'ENABLED'
          AND segments.date = YESTERDAY
        ORDER BY metrics.cost_micros DESC
    """
)
```

**What You Get:**
- All PMax campaigns
- Yesterday's metrics
- Sorted by spend (highest first)

**Calculate ROAS:**
```python
for campaign in result['results']:
    cost = int(campaign['metrics']['costMicros'])
    revenue = int(campaign['metrics']['conversionsValue'])
    roas = revenue / cost if cost > 0 else 0
    print(f"{campaign['campaign']['name']}: ROAS = {roas:.2f}")
```

---

### Use Case 2: Budget Pacing Alert

**Scenario:** Check if today's spend is on track

```python
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

result = await run_gaql_query(
    account_id="1234567890",
    query=f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign_budget.amount_micros,
          metrics.cost_micros
        FROM campaign
        WHERE
          campaign.status = 'ENABLED'
          AND segments.date = '{today}'
    """
)
```

**Analyze Pacing:**
```python
for campaign in result['results']:
    budget = int(campaign['campaignBudget']['amountMicros'])
    spend = int(campaign['metrics']['costMicros'])
    pacing = (spend / budget) * 100 if budget > 0 else 0

    if pacing < 50:
        print(f"⚠️ {campaign['campaign']['name']}: Under-pacing ({pacing:.0f}%)")
    elif pacing > 150:
        print(f"🔥 {campaign['campaign']['name']}: Over-pacing ({pacing:.0f}%)")
    else:
        print(f"✅ {campaign['campaign']['name']}: On track ({pacing:.0f}%)")
```

---

### Use Case 3: Product Performance Analysis

**Scenario:** Find top-selling products in a PMax campaign

```python
result = await run_gaql_query(
    account_id="1234567890",
    query="""
        SELECT
          segments.product_title,
          segments.product_item_id,
          segments.product_custom_attribute0,
          metrics.conversions_value,
          metrics.conversions,
          metrics.cost_micros
        FROM shopping_performance_view
        WHERE
          campaign.id = 9876543210
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.conversions_value DESC
        LIMIT 20
    """
)
```

**What You Get:**
- Top 20 products by revenue
- Product IDs and titles
- Custom labels (for filtering)
- Revenue, conversions, spend

**Insights:**
- Which products drive the most revenue
- Products to prioritize in GMC
- Products to increase inventory for

---

### Use Case 4: ROAS Achievement Check

**Scenario:** See if campaigns are meeting their ROAS targets

```python
result = await run_gaql_query(
    account_id="1234567890",
    query="""
        SELECT
          campaign.id,
          campaign.name,
          campaign.maximize_conversion_value.target_roas,
          metrics.cost_micros,
          metrics.conversions_value
        FROM campaign
        WHERE
          campaign.advertising_channel_type = 'PERFORMANCE_MAX'
          AND campaign.status = 'ENABLED'
          AND campaign.maximize_conversion_value.target_roas > 0
          AND segments.date DURING LAST_30_DAYS
        ORDER BY campaign.name
    """
)
```

**Analyze ROAS Achievement:**
```python
for campaign in result['results']:
    target_roas = campaign['campaign']['maximizeConversionValue']['targetRoas']
    cost = int(campaign['metrics']['costMicros'])
    revenue = int(campaign['metrics']['conversionsValue'])
    actual_roas = revenue / cost if cost > 0 else 0
    achievement = (actual_roas / target_roas) * 100

    status = "✅" if achievement >= 100 else "⚠️"
    print(f"{status} {campaign['campaign']['name']}")
    print(f"   Target: {target_roas:.2f}, Actual: {actual_roas:.2f}, Achievement: {achievement:.0f}%")
```

---

## 💡 Common GAQL Patterns

### Date Filtering

```sql
-- Last 7 days
WHERE segments.date DURING LAST_7_DAYS

-- Last 30 days
WHERE segments.date DURING LAST_30_DAYS

-- This month
WHERE segments.date DURING THIS_MONTH

-- Yesterday
WHERE segments.date = YESTERDAY

-- Specific date
WHERE segments.date = '2025-11-07'

-- Date range
WHERE segments.date BETWEEN '2025-11-01' AND '2025-11-30'
```

### Campaign Filtering

```sql
-- Performance Max only
WHERE campaign.advertising_channel_type = 'PERFORMANCE_MAX'

-- Enabled campaigns
WHERE campaign.status = 'ENABLED'

-- Specific campaign
WHERE campaign.id = 9876543210

-- Multiple campaigns
WHERE campaign.id IN (111111, 222222, 333333)

-- Campaign name pattern (not supported - use API filtering)
```

### Ordering and Limiting

```sql
-- Sort by spend (highest first)
ORDER BY metrics.cost_micros DESC

-- Sort by ROAS (need to calculate separately)
ORDER BY metrics.conversions_value DESC

-- Multiple sorts
ORDER BY
  metrics.conversions_value DESC,
  metrics.cost_micros DESC

-- Limit results
LIMIT 100
```

---

## 🔒 Tips and Best Practices

### 1. Always Use Date Filters
❌ Bad: Retrieves all historical data
```sql
SELECT campaign.name, metrics.cost_micros
FROM campaign
WHERE campaign.status = 'ENABLED'
```

✅ Good: Only recent data
```sql
SELECT campaign.name, metrics.cost_micros
FROM campaign
WHERE
  campaign.status = 'ENABLED'
  AND segments.date DURING LAST_7_DAYS
```

### 2. Use Appropriate LIMIT
```sql
-- Always limit results to prevent huge responses
LIMIT 100  -- or 1000 for detailed analysis
```

### 3. Check for Zero Values
```python
# Avoid division by zero
roas = revenue / cost if cost > 0 else 0
cpa = cost / conversions if conversions > 0 else 0
```

### 4. Handle Micros Correctly
```python
# All monetary values are in micros
cost_dollars = cost_micros / 1_000_000
budget_thb = budget_micros / 1_000_000

# ROAS calculation (both in micros, so ratio is correct)
roas = revenue_micros / cost_micros
```

---

## 📈 Common Calculations

### ROAS (Return on Ad Spend)
```python
roas = metrics.conversions_value / metrics.cost_micros
# Both in micros, so result is already correct
# Example: 3.5 = $3.50 revenue per $1 spent
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

### CTR (Click-Through Rate)
```python
# Already available as metrics.ctr (percentage)
ctr = metrics.ctr

# Or calculate manually
ctr = (metrics.clicks / metrics.impressions) * 100
```

### Budget Utilization
```python
daily_budget = campaign_budget.amount_micros
spend_today = metrics.cost_micros
utilization = (spend_today / daily_budget) * 100
```

### Average Order Value (AOV)
```python
aov = metrics.conversions_value / metrics.conversions
```

---

## 🚧 Known Limitations

1. ⚠️ **No wildcard campaign name search** - Use specific IDs or fetch all
2. ⚠️ **ROAS not directly sortable** - Must calculate client-side
3. ⚠️ **Limited historical budget data** - Shows current budget for all dates
4. ⚠️ **Pagination required for large datasets** - Max 10,000 results per page

---

## ✅ Phase 6 Checklist

| Task | Status |
|------|--------|
| Create GAQL Recipe Book | ✅ |
| Document 20 query recipes | ✅ |
| Performance Max recipes | ✅ |
| Budget & pacing recipes | ✅ |
| Asset group recipes | ✅ |
| Shopping product recipes | ✅ |
| Campaign comparison recipes | ✅ |
| Diagnostic recipes | ✅ |
| Advanced recipes | ✅ |
| Implement run_gaql_query tool | ✅ |
| Error handling | ✅ |
| Usage examples | ✅ |
| Tips and best practices | ✅ |

**Phase 6 Complete!** 🎉

Ready for Phase 7: Guardrails and Dry-Run Mode 🚀

---

## 🔗 Resources

### Google Documentation:
- [GAQL Grammar](https://developers.google.com/google-ads/api/docs/query/grammar)
- [Google Ads API Fields](https://developers.google.com/google-ads/api/fields/v19/overview)
- [Campaign Resource](https://developers.google.com/google-ads/api/fields/v19/campaign)
- [Metrics Reference](https://developers.google.com/google-ads/api/fields/v19/metrics)
- [Segments Reference](https://developers.google.com/google-ads/api/fields/v19/segments)

### Project Files:
- `docs/GAQL_RECIPES.md` - Complete query recipe book
- `google_ads_server.py` - MCP server with run_gaql_query tool

---

**Built with ❤️ for huge8888/mcp-google-ads**
