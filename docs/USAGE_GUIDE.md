# Real-World Usage Guide

Complete guide for using the Google Ads MCP Agent with Claude in production scenarios.

## Table of Contents

- [Getting Started](#getting-started)
- [Common Workflows](#common-workflows)
- [Prompt Templates](#prompt-templates)
- [Real-World Examples](#real-world-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Setup Checklist

Before using the MCP agent with Claude, ensure:

1. ✅ MCP servers configured in Claude settings
2. ✅ Google Ads authentication completed
3. ✅ `.env` file configured with guardrails
4. ✅ Test queries run successfully

### MCP Server Configuration

Add to your Claude configuration (usually `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "python",
      "args": ["/full/path/to/mcp-google-ads/google_ads_server.py"],
      "env": {
        "GOOGLE_ADS_CLIENT_SECRET_PATH": "/path/to/client_secret.json",
        "GOOGLE_ADS_TOKEN_PATH": "/path/to/token.pickle",
        "DRY_RUN": "false",
        "REQUIRE_CONFIRMATION": "true"
      }
    },
    "google-merchant-center": {
      "command": "python",
      "args": ["/full/path/to/mcp-google-ads/mcp-gmc/gmc_server.py"],
      "env": {
        "GOOGLE_ADS_CLIENT_SECRET_PATH": "/path/to/client_secret.json",
        "GOOGLE_ADS_TOKEN_PATH": "/path/to/token.pickle"
      }
    }
  }
}
```

---

## Common Workflows

### Workflow 1: Create New Performance Max Campaign

**Goal:** Launch a new Performance Max campaign for a product promotion

**Steps:**

1. **Upload products to Google Merchant Center**
2. **Create campaign in Google Ads**
3. **Monitor initial performance**
4. **Optimize based on results**

**Example Conversation with Claude:**

```
User: I need to create a new Performance Max campaign for our November sunglasses promotion in Thailand.
      Budget is 1,500 THB per day, target ROAS of 2.5, and I want to use products with the custom label "promo_nov2025".

Claude: I'll help you create this campaign. Let me first upload the products to Google Merchant Center,
        then create the Performance Max campaign.

        [Uses insert_product from GMC server to add products]
        [Uses create_pmax_campaign from Google Ads server]

        ✅ Campaign created successfully:
        - Campaign: "SEW | Sunglasses PMax | TH | 2025-11"
        - Budget: 1,500 THB/day
        - Target ROAS: 2.5
        - Status: PAUSED (for your review)
        - Merchant Center linked with feed_label: "promo_nov2025"

        The campaign is currently paused. Would you like me to:
        1. Enable it now
        2. Show you the campaign details first
        3. Run a safety check before enabling

User: Run a safety check first.

Claude: [Uses GAQL query to check campaign configuration]

        Safety check results:
        ✅ Budget configured correctly
        ✅ Merchant Center linked
        ✅ Asset group created
        ✅ Feed label matches products (15 products found)
        ⚠️ Conversion tracking not verified - please check in Google Ads UI

        Everything looks good! Would you like me to enable the campaign?

User: Yes, enable it.

Claude: [Uses enable_campaign with safety_check=true]

        ✅ Campaign enabled successfully!
        I'll monitor the performance for you. I recommend checking back in 24 hours.
```

---

### Workflow 2: Daily Performance Review

**Goal:** Review yesterday's performance and make adjustments

**Example Conversation:**

```
User: Good morning! Please review yesterday's performance for all my Performance Max campaigns.

Claude: Good morning! Let me pull yesterday's performance data.

        [Uses run_gaql_query with GAQL Recipe 1]

        📊 Performance Max Campaigns - Yesterday (2025-11-06)

        1. SEW | Sunglasses PMax | TH | 2025-11
           - Spend: ฿1,487 (99% of budget)
           - Conversions: 42
           - Revenue: ฿3,721
           - ROAS: 2.50 ⬆️ (Target: 2.50) ✅
           - Impressions: 12,453
           - Clicks: 387

        2. SEW | Watches PMax | TH | 2025-11
           - Spend: ฿2,156 (144% of budget) ⚠️
           - Conversions: 28
           - Revenue: ฿4,890
           - ROAS: 2.27 ⬇️ (Target: 2.50) ⚠️
           - Impressions: 18,921
           - Clicks: 512

        🎯 Summary:
        - Total spend: ฿3,643
        - Total revenue: ฿8,611
        - Overall ROAS: 2.36

        📌 Recommendations:
        1. Sunglasses campaign is performing perfectly - no changes needed
        2. Watches campaign:
           - Over-pacing by 44% - consider reducing budget to ฿1,500
           - ROAS below target - suggest increasing target ROAS to 2.8 to improve profitability

        Would you like me to make these adjustments?

User: Yes, adjust the watches campaign.

Claude: [Uses update_campaign_budget and set_target_roas]

        ✅ Adjusted Watches campaign:
        - Reduced budget from ฿1,500 to ฿1,300/day (13% reduction)
        - Increased target ROAS from 2.5 to 2.8

        These changes will help:
        - Control spend and prevent budget overrun
        - Improve profitability by bidding more conservatively

        I'll monitor today's performance and update you tomorrow!
```

---

### Workflow 3: Product Price Update & Campaign Management

**Goal:** Run a flash sale by updating product prices and monitoring campaign

**Example Conversation:**

```
User: We're running a flash sale on all sunglasses for the next 48 hours.
      Regular price is ฿1,200, sale price is ฿999. Please update all sunglasses products.

Claude: I'll update the prices for all sunglasses products in Google Merchant Center.

        [Uses list_products from GMC server to find all sunglasses]
        [Uses update_price for each product]

        ✅ Updated 15 sunglasses products:
        - Regular price: ฿1,200
        - Sale price: ฿999 (17% off)
        - Sale period: 2025-11-07 00:00 to 2025-11-09 23:59

        💡 Recommendation:
        Since you're running a sale, I suggest temporarily increasing the campaign budget
        to take advantage of higher conversion rates during the promotion.

        Current budget: ฿1,500/day
        Suggested budget: ฿2,500/day (+67%)

        Would you like me to increase the budget?

User: Yes, but let's be conservative. Increase to ฿2,000/day.

Claude: [Uses update_campaign_budget]

        ✅ Updated budget to ฿2,000/day

        I'll monitor the campaign closely during the sale period.
        After the sale ends on Nov 9, I can:
        1. Revert prices back to ฿1,200
        2. Reduce budget back to ฿1,500/day

        Would you like me to set a reminder for this?

User: Yes, remind me on Nov 9 at 9 AM.

Claude: ✅ Reminder set! On Nov 9 at 9 AM, I'll:
        - Notify you that the sale is ending
        - Suggest reverting prices and budget
        - Wait for your confirmation before making changes

        For now, let me set up monitoring for the flash sale...
        [Sets up daily check for sale performance]
```

---

### Workflow 4: Budget Pacing & Optimization

**Goal:** Monitor budget pacing throughout the day and adjust

**Example Conversation:**

```
User: It's 2 PM. How is today's budget pacing looking?

Claude: Let me check current budget pacing for all campaigns.

        [Uses run_gaql_query with GAQL Recipe 5]

        ⏰ Budget Pacing Check - 2025-11-07 14:00

        1. SEW | Sunglasses PMax | TH | 2025-11
           Budget: ฿1,500/day
           Spent so far: ฿875 (58%)
           Expected at this time: ฿875 (58%) ✅
           Status: On track

        2. SEW | Watches PMax | TH | 2025-11
           Budget: ฿1,300/day
           Spent so far: ฿456 (35%)
           Expected at this time: ฿758 (58%) ⚠️
           Status: Under-pacing by 40%

        📊 Analysis:
        - Sunglasses: Perfect pacing
        - Watches: Significantly under-pacing

        💡 Possible reasons for under-pacing (Watches):
        - ROAS target too high (2.8) limiting impressions
        - Inventory issues in GMC
        - Low search volume today

        Would you like me to investigate further?

User: Yes, check what's going on with the watches campaign.

Claude: [Uses multiple GAQL queries to diagnose]

        🔍 Diagnosis for Watches campaign:

        1. Inventory Check:
           [Uses list_products from GMC]
           ⚠️ Found issue: 8 out of 12 watch products show "out of stock"

        2. ROAS Performance:
           Current ROAS: 3.2 (exceeds target of 2.8) ✅
           Issue: High ROAS means Google is being very conservative with bids

        3. Product Performance:
           [Uses GAQL Recipe 10]
           Only 4 products actively getting impressions

        📝 Recommendations:
        1. Update inventory status for the 8 out-of-stock products in GMC
        2. Temporarily reduce ROAS target from 2.8 to 2.5 to allow more volume
        3. Consider adding more watch products to GMC

        Which would you like me to do?

User: Let's reduce the ROAS target to 2.5 for now. I'll check inventory later.

Claude: [Uses set_target_roas]

        ✅ Reduced target ROAS from 2.8 to 2.5 for Watches campaign

        This should help increase volume while maintaining profitability.
        I'll check pacing again in 2 hours and update you.
```

---

## Prompt Templates

### Template 1: Create Campaign

```
Create a Performance Max campaign for [PRODUCT_LINE] in [COUNTRY].

Details:
- Daily budget: [AMOUNT] [CURRENCY]
- Target ROAS: [ROAS_VALUE]
- Products: Use custom label "[FEED_LABEL]"
- Start date: [DATE]
- Status: Paused (for review)

Campaign name format: [BRAND] | [PRODUCT] PMax | [COUNTRY] | [MONTH-YEAR]
```

**Example:**
```
Create a Performance Max campaign for sunglasses in Thailand.

Details:
- Daily budget: 1500 THB
- Target ROAS: 2.5
- Products: Use custom label "promo_nov2025"
- Start date: 2025-11-10
- Status: Paused (for review)

Campaign name format: SEW | Sunglasses PMax | TH | 2025-11
```

---

### Template 2: Daily Performance Review

```
Review yesterday's performance for all Performance Max campaigns.

Include:
- Spend vs budget
- Conversions and revenue
- ROAS vs target
- Recommendations for optimization

If any campaign is significantly over/under performing, suggest specific actions.
```

---

### Template 3: Budget Adjustment

```
[Campaign name] is [over-pacing/under-pacing] by [PERCENTAGE]%.

Current budget: [CURRENT_AMOUNT] [CURRENCY]/day
Suggested new budget: [NEW_AMOUNT] [CURRENCY]/day

Please adjust the budget and explain the expected impact.
```

---

### Template 4: Product Price Update

```
Update prices for all [PRODUCT_CATEGORY] products:
- Regular price: [PRICE] [CURRENCY]
- Sale price: [SALE_PRICE] [CURRENCY]
- Sale period: [START_DATE] to [END_DATE]

After updating, suggest any campaign adjustments needed for the sale period.
```

---

### Template 5: Campaign Troubleshooting

```
[Campaign name] is experiencing [ISSUE].

Please:
1. Diagnose the root cause
2. Check campaign configuration, products, and bidding
3. Provide specific recommendations
4. Implement approved fixes
```

---

## Real-World Examples

### Example 1: E-commerce Scaling Strategy

**Scenario:** Online sunglasses store wants to scale from ฿5,000/day to ฿20,000/day

**Conversation:**

```
User: I want to scale our sunglasses campaign from ฿5,000/day to ฿20,000/day over the next 2 weeks.
      How should we approach this?

Claude: Great question! Scaling 4x in 2 weeks is aggressive but achievable. Here's a safe scaling plan:

        📈 Recommended Scaling Strategy:

        Week 1: Conservative scaling (+50% total)
        - Day 1-2: ฿5,000 → ฿6,250 (+25%)
        - Day 3-4: ฿6,250 → ฿7,500 (+20%)
        - Monitor ROAS closely, pause if drops below 2.2

        Week 2: Aggressive scaling (+165% total from Week 1)
        - Day 5-7: ฿7,500 → ฿10,000 (+33%)
        - Day 8-10: ฿10,000 → ฿15,000 (+50%)
        - Day 11-14: ฿15,000 → ฿20,000 (+33%)

        ⚠️ Guardrails:
        - If ROAS drops below 2.0 at any point, pause scaling
        - If ROAS stays above 2.8, scale faster
        - Monitor conversion tracking daily

        💡 To support this scaling, I recommend:
        1. Ensure at least 50 products active in GMC
        2. Add fresh product images this week
        3. Enable "Maximize Conversion Value" to let Google optimize
        4. Keep target ROAS at 2.5 (don't increase during scaling)

        Would you like me to start with Day 1's increase to ฿6,250?

User: Yes, let's do it. But I want you to check performance every morning and suggest adjustments.

Claude: [Uses update_campaign_budget]

        ✅ Increased budget to ฿6,250/day (+25%)

        📅 Set up daily monitoring:
        - Every morning at 9 AM (your timezone)
        - I'll review previous day's performance
        - Suggest budget adjustments based on ROAS
        - Proceed with scaling plan if performance is good

        I'll also watch for:
        - Conversion tracking issues
        - Product disapprovals in GMC
        - Budget pacing problems
        - ROAS trends

        See you tomorrow morning at 9 AM for Day 1 review!
```

---

### Example 2: Multi-Campaign Management

**Scenario:** Managing 10 Performance Max campaigns across different product categories

**Conversation:**

```
User: I have 10 Performance Max campaigns running. Give me a quick health check on all of them.

Claude: [Uses run_gaql_query with custom query for all campaigns]

        🏥 Campaign Health Check - 10 Campaigns

        ✅ Healthy (6 campaigns):
        1. Sunglasses - ROAS 2.8, Budget 98%, ✅
        2. Watches - ROAS 2.6, Budget 95%, ✅
        3. Bags - ROAS 3.1, Budget 102%, ✅
        4. Wallets - ROAS 2.9, Budget 87%, ✅
        5. Belts - ROAS 2.7, Budget 91%, ✅
        6. Shoes - ROAS 2.5, Budget 99%, ✅

        ⚠️ Needs Attention (3 campaigns):
        7. Hats - ROAS 1.9 (below 2.0), Budget 156% ⚠️
           Action: Reduce budget by 30% and increase ROAS target

        8. Scarves - ROAS 2.4, Budget 42% ⚠️
           Action: Reduce ROAS target to increase volume

        9. Accessories - ROAS 3.5, Budget 38% ⚠️
           Action: Consider increasing budget to capture more volume

        🔴 Critical (1 campaign):
        10. Jewelry - ROAS 1.2, Budget 189% 🔴
            Action: PAUSE immediately and investigate

        📊 Summary:
        - 6 campaigns performing well
        - 3 campaigns need optimization
        - 1 campaign needs immediate action

        Would you like me to:
        A) Pause the Jewelry campaign immediately
        B) Optimize the 3 "needs attention" campaigns
        C) Both A and B

User: Both A and B please.

Claude: [Executes multiple actions]

        1. ✅ PAUSED Jewelry campaign
           - Was spending 89% over budget
           - ROAS only 1.2 (losing money)
           - Will investigate and report back

        2. ✅ Optimized Hats campaign:
           - Reduced budget from ฿2,000 to ฿1,400/day (-30%)
           - Increased ROAS target from 2.5 to 3.0
           - Expected impact: Better profitability, controlled spend

        3. ✅ Optimized Scarves campaign:
           - Reduced ROAS target from 3.2 to 2.8
           - Expected impact: 50-70% more volume

        4. ✅ Optimized Accessories campaign:
           - Increased budget from ฿800 to ฿1,200/day (+50%)
           - ROAS is strong, should capture more volume

        🔍 Now investigating Jewelry campaign...
        [Runs diagnostic queries]

        📝 Jewelry Campaign Issues Found:
        1. ⚠️ All 15 jewelry products showing "limited" status in GMC
        2. ⚠️ Missing GTINs for most products
        3. ⚠️ Target ROAS set too low (1.5)

        Recommended fixes:
        1. Update products in GMC with GTINs
        2. Fix product data quality issues
        3. Increase ROAS target to 3.0 (jewelry typically has higher margins)

        I'll send you a detailed product list that needs GTINs.
```

---

## Best Practices

### 1. Always Test in Dry-Run First

```
User: I want to increase budget for all campaigns by 50%.

Claude: That's a significant change affecting multiple campaigns.
        Let me first run this in dry-run mode to show you exactly what will happen.

        [Enables DRY_RUN mode]
        [Simulates budget updates]

        📋 Dry-Run Results: What WOULD happen

        Would update 10 campaigns:
        1. Sunglasses: ฿1,500 → ฿2,250 (+฿750)
        2. Watches: ฿1,300 → ฿1,950 (+฿650)
        ... [8 more]

        Total daily budget increase: +฿5,825/day
        Monthly impact: +฿174,750/month

        ⚠️ Warnings:
        - 2 campaigns would exceed MAX_BUDGET limit
        - Total monthly spend would be ฿524,250

        This looks okay. Shall I proceed with the actual changes?
```

### 2. Monitor Actively, Adjust Conservatively

```
# Daily review routine
User: Good morning! What's my daily briefing?

Claude: Good morning! Here's your Performance Max daily briefing:

        📊 Yesterday's Performance (Nov 6):
        [Performance data]

        🎯 Today's Focus:
        [Key metrics to watch]

        ⚡ Actions Needed:
        [Specific recommendations]

        I'll check back with you at 2 PM for mid-day pacing review.
```

### 3. Use GAQL Recipes for Insights

```
User: I want to see which products are driving the most revenue.

Claude: [Uses GAQL Recipe 10 - Product Performance]

        🏆 Top Revenue Products (Last 30 Days):

        1. Classic Black Sunglasses (SKU-001)
           Revenue: ฿45,230 | Conv: 123 | ROAS: 3.2

        2. Sport Sunglasses Blue (SKU-045)
           Revenue: ฿38,920 | Conv: 98 | ROAS: 2.9

        [More products...]

        💡 Insight:
        Your top 5 products account for 67% of total revenue.
        Consider:
        - Increasing stock for top sellers
        - Creating dedicated campaigns for best performers
        - Finding similar products to add to catalog
```

### 4. Document Major Changes

```
User: Increase the sunglasses campaign budget to ฿3,000/day.

Claude: [Uses update_campaign_budget]

        ✅ Updated budget to ฿3,000/day

        📝 Change Log Entry:
        - Date: 2025-11-07 14:30
        - Campaign: SEW | Sunglasses PMax | TH | 2025-11
        - Action: Budget increase
        - Old value: ฿1,500/day
        - New value: ฿3,000/day (+100%)
        - Reason: Scaling successful campaign
        - Expected outcome: 2x volume at current ROAS (2.8)

        I'll monitor performance and report back in 24 hours.
```

---

## Troubleshooting

### Issue 1: Campaign Not Spending

**Symptoms:**
- Budget utilization < 50%
- Low impressions
- High ROAS but low spend

**Diagnosis Steps:**

```
User: My campaign is barely spending. Budget is ฿2,000 but only spending ฿400/day.

Claude: Let me run a diagnostic on your campaign.

        [Runs multiple checks]

        🔍 Diagnostic Results:

        1. ROAS Target: 4.5 (very high) ⚠️
           - Google can't find enough conversions at this target
           - Recommendation: Reduce to 2.5-3.0

        2. Product Status:
           - 8 products active ✅
           - 12 products "limited" or "disapproved" ⚠️
           - Recommendation: Fix product issues in GMC

        3. Targeting:
           - Location: Thailand ✅
           - Language: Thai ✅
           - No geo exclusions ✅

        4. Budget vs Recommendations:
           - Your budget: ฿2,000/day
           - Google's recommendation: ฿650/day
           - Issue: Budget too high for current targeting/products

        💡 Solution:
        Option A: Reduce ROAS target from 4.5 to 2.8
        Option B: Add more products to GMC (target: 30+ products)
        Option C: Both A and B (recommended)

        Which would you like to try?
```

### Issue 2: ROAS Below Target

**Symptoms:**
- Spending budget
- Getting conversions
- ROAS below target

**Diagnosis Steps:**

```
User: My ROAS is 1.8 but I need it to be 2.5.

Claude: Let me analyze what's causing the low ROAS.

        [Uses multiple GAQL queries]

        📉 ROAS Analysis:

        Current Performance:
        - ROAS: 1.8 (need: 2.5)
        - Gap: -28%

        Breaking down by dimension:

        1. Device Performance:
           - Desktop: ROAS 2.9 ✅
           - Mobile: ROAS 1.4 ❌
           - Tablet: ROAS 2.1 ✅
           Problem: Mobile is dragging down overall ROAS

        2. Product Performance:
           - Top 5 products: ROAS 3.2 ✅
           - Bottom 10 products: ROAS 0.9 ❌
           Problem: Low-performing products eating budget

        3. Time of Day:
           - 9AM-5PM: ROAS 2.6 ✅
           - 5PM-12AM: ROAS 1.3 ❌
           Problem: Evening performance is poor

        🎯 Recommendations:
        1. Exclude bottom 10 products (remove custom labels)
        2. Increase ROAS target to 3.0 (force better performance)
        3. Consider mobile bid adjustment (-30%)

        Which approach would you prefer?
```

---

## Advanced Workflows

### Workflow 5: Automated Performance Monitoring

**Setup an automated daily report:**

```
User: Set up an automated daily performance report that I receive every morning.

Claude: I'll set up an automated daily monitoring system. Here's what it will include:

        📧 Daily Performance Report (Every morning at 9 AM):

        1. Performance Summary:
           - All campaigns performance vs targets
           - Spend vs budget
           - ROAS achievement

        2. Alerts:
           - Any campaign with ROAS < 2.0
           - Any campaign over-pacing > 120%
           - Any campaign under-pacing < 50%
           - Product disapprovals in GMC

        3. Recommendations:
           - Suggested budget adjustments
           - ROAS target changes
           - Product updates needed

        4. Weekly Trends (on Mondays):
           - Week-over-week performance
           - Best/worst performing products
           - Scaling opportunities

        This report will run automatically. You can:
        - Reply to make suggested changes
        - Ask for deeper analysis
        - Request specific GAQL queries

        Would you like me to activate this?
```

---

## Summary

This guide covers the most common real-world scenarios for using the Google Ads MCP Agent with Claude. Key takeaways:

1. **Start conversations naturally** - Claude understands context and can help structure complex tasks
2. **Use dry-run mode** for major changes
3. **Monitor actively** - Daily reviews prevent issues
4. **Leverage GAQL recipes** for insights
5. **Let Claude help diagnose** issues before making changes
6. **Document changes** for audit trail
7. **Set up automation** for routine tasks

For more examples and recipes, see:
- `docs/GAQL_RECIPES.md` - Query recipes
- `docs/SAFE_ROLLOUT_CHECKLIST.md` - Safe deployment
- `PHASE*_COMPLETE.md` - Feature documentation

**Happy automating!** 🚀
