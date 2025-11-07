# ✅ Phase 2 Complete - Performance Max Campaign Implementation

## 🚀 Phase 2 Summary

Phase 2 เพิ่ม **implementation จริง** สำหรับการสร้าง Performance Max campaigns!

### สิ่งที่ทำเสร็จ:

1. ✅ **Performance Max Campaign Module** (`mutate/pmax.py`)
   - สร้าง class `PerformanceMaxCampaign` สำหรับจัดการ API calls
   - 410+ บรรทัดของ production-ready code

2. ✅ **Full Campaign Creation** (`create_pmax_campaign_full`)
   - สร้าง Campaign + Budget ในขั้นตอนเดียว
   - รองรับ Asset Group creation
   - รองรับ Merchant Center integration
   - Error handling ครบถ้วน

3. ✅ **MCP Tool Integration**
   - อัพเดต `create_pmax_campaign` ใน `google_ads_server.py`
   - เชื่อมกับ implementation จริง
   - Error handling และ validation

4. ✅ **Comprehensive Tests** (14 new tests)
   - Unit tests สำหรับทุก function
   - Mock API responses
   - Error scenario coverage
   - **Total: 57 tests passing**

---

## 📦 New Files & Updates

### Files Created:
```
mutate/pmax.py                  # 410 lines - PMax implementation
tests/test_pmax.py              # 380 lines - Unit tests
PHASE2_COMPLETE.md              # This file
```

### Files Updated:
```
google_ads_server.py            # Updated create_pmax_campaign tool
```

---

## 🎯 Features Implemented

### 1. Campaign Budget Creation
```python
_create_campaign_budget(
    customer_id="1234567890",
    amount_micros=1500000000,
    budget_name="Campaign Budget"
)
# Returns: "customers/1234567890/campaignBudgets/111111"
```

**Features:**
- Creates shared or non-shared budget
- Standard delivery method
- Automatic budget naming

### 2. Campaign Creation
```python
create_campaign(
    customer_id="1234567890",
    campaign_name="My PMax Campaign",
    budget_amount_micros=1500000000,
    target_roas=2.5,
    start_date="2025-11-10",
    end_date="2025-12-31",
    status="PAUSED"
)
```

**Features:**
- Performance Max channel type
- Maximize Conversion Value bidding strategy
- Optional target ROAS
- Optional date range (start/end)
- Configurable status (PAUSED/ENABLED)

### 3. Asset Group Creation
```python
create_asset_group(
    customer_id="1234567890",
    campaign_resource_name="customers/1234567890/campaigns/222222",
    asset_group_name="Product Assets",
    final_urls=["https://example.com/products"]
)
```

**Features:**
- Links to campaign
- Supports multiple final URLs
- Auto-enabled status

### 4. Merchant Center Integration
```python
attach_merchant_center_feed(
    customer_id="1234567890",
    campaign_resource_name="customers/1234567890/campaigns/222222",
    merchant_center_id="123456789",
    feed_label="promo_nov2025"
)
```

**Features:**
- Links GMC account to campaign
- Optional feed label filtering
- Enable local inventory ads

### 5. Full Campaign Creation (All-in-One)
```python
create_pmax_campaign_full(
    credentials=creds,
    headers=headers,
    account_id="1234567890",
    campaign_name="SEW | Sunglasses PMax | TH | 2025-11",
    daily_budget_currency=1500,    # ใช้ currency units
    target_roas=2.5,
    merchant_center_id="123456789",
    feed_label="promo_nov2025",
    start_date="2025-11-10",
    status="PAUSED",
    final_url="https://example.com/products"
)
```

**Features:**
- Creates budget + campaign + asset group + GMC link
- Flexible budget input (micros or currency)
- Automatic customer ID formatting
- Comprehensive error handling

---

## 🧪 Test Coverage

### Test Summary:
```
✅ 14 new tests for Performance Max operations
✅ 43 existing tests (from Phase 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Total: 57 tests passing
```

### Tests Added:

#### `TestPerformanceMaxCampaign` (9 tests)
- ✅ `test_init` - Class initialization
- ✅ `test_create_campaign_budget` - Budget creation
- ✅ `test_create_campaign_minimal` - Minimal campaign
- ✅ `test_create_campaign_with_roas` - Campaign with ROAS
- ✅ `test_create_campaign_with_dates` - Campaign with dates
- ✅ `test_create_asset_group` - Asset group creation
- ✅ `test_attach_merchant_center` - GMC integration
- ✅ `test_create_campaign_error_budget` - Budget error handling
- ✅ `test_create_campaign_error_campaign` - Campaign error handling

#### `TestCreatePMaxCampaignFull` (5 tests)
- ✅ `test_create_with_currency` - Using currency units
- ✅ `test_create_with_micros` - Using micros
- ✅ `test_create_with_asset_group` - With asset group
- ✅ `test_create_with_merchant_center` - With GMC
- ✅ `test_create_without_budget` - Error when no budget

---

## 🔧 Usage Examples

### Example 1: Minimal Campaign (PAUSED, no Merchant Center)
```python
result = await create_pmax_campaign(
    account_id="1234567890",
    campaign_name="Test Campaign",
    daily_budget_currency=1000,
)
```

**Response:**
```json
{
  "success": true,
  "campaign_resource_name": "customers/1234567890/campaigns/222222",
  "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
  "campaign_name": "Test Campaign",
  "status": "PAUSED"
}
```

### Example 2: Full PMax with Everything
```python
result = await create_pmax_campaign(
    account_id="1234567890",
    campaign_name="SEW | Sunglasses PMax | TH | 2025-11",
    daily_budget_currency=1500,
    target_roas=2.5,
    merchant_center_id="123456789",
    feed_label="promo_nov2025",
    start_date="2025-11-10",
    end_date="2025-12-31",
    status="PAUSED",
    final_url="https://example.com/products"
)
```

**Response:**
```json
{
  "success": true,
  "campaign_resource_name": "customers/1234567890/campaigns/222222",
  "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
  "asset_group_resource_name": "customers/1234567890/assetGroups/333333",
  "campaign_name": "SEW | Sunglasses PMax | TH | 2025-11",
  "status": "PAUSED",
  "asset_group_name": "SEW | Sunglasses PMax | TH | 2025-11 Assets",
  "merchant_center_attached": true,
  "merchant_center_id": "123456789",
  "feed_label": "promo_nov2025",
  "target_roas": 2.5,
  "start_date": "2025-11-10",
  "end_date": "2025-12-31"
}
```

### Example 3: Using with MCP (from Claude)
```
User: Create a Performance Max campaign for my sunglasses promo

Claude: I'll create that campaign for you.

Tool: create_pmax_campaign
Parameters:
  account_id: "1234567890"
  campaign_name: "Sunglasses Promo PMax"
  daily_budget_currency: 1500
  target_roas: 2.5
  merchant_center_id: "123456789"
  feed_label: "sunglasses_promo"
  status: "PAUSED"

Result: Successfully created campaign with resource name customers/1234567890/campaigns/222222
```

---

## ⚡ API Calls Made

When creating a full campaign, the following API calls are made:

```
1. POST /customers/{customer_id}/campaignBudgets:mutate
   └─ Creates campaign budget

2. POST /customers/{customer_id}/campaigns:mutate
   └─ Creates Performance Max campaign

3. POST /customers/{customer_id}/assetGroups:mutate  (if final_url provided)
   └─ Creates asset group

4. POST /customers/{customer_id}/campaigns:mutate  (if merchant_center_id provided)
   └─ Updates campaign with shopping settings
```

**Total API Calls:** 2-4 (depending on options)

---

## 🔒 Error Handling

### Validation Errors
```json
{
  "error": "Validation error",
  "message": "Either daily_budget_micros or daily_budget_currency must be provided"
}
```

### API Errors
```json
{
  "error": "Failed to create campaign",
  "message": "INVALID_ARGUMENT: Campaign name is too long",
  "type": "Exception"
}
```

### Common Error Scenarios:
1. ❌ No budget provided → ValidationError
2. ❌ Invalid customer ID → API Error
3. ❌ Budget creation fails → Exception with details
4. ❌ Campaign creation fails → Exception with details
5. ❌ Invalid Merchant Center ID → API Error

---

## 📊 Performance & Best Practices

### Performance:
- ⚡ 2-4 API calls per campaign creation
- ⚡ Automatic retry on auth token expiration
- ⚡ Parallel operations where possible

### Best Practices:
1. ✅ Always start campaigns as **PAUSED**
2. ✅ Use **currency_to_micros** for budget conversion
3. ✅ Validate dates before API calls
4. ✅ Check campaign in Ads UI before enabling
5. ✅ Use feed labels for product filtering

---

## 🚧 Known Limitations

1. ⚠️ **No targeting yet** - country_codes and language_codes accepted but not implemented
2. ⚠️ **Basic asset group** - only final URLs, no text/images yet
3. ⚠️ **No bid strategy options** - only Maximize Conversion Value with optional ROAS
4. ⚠️ **No campaign settings** - advanced settings not yet implemented

These will be addressed in future phases or can be set manually in Google Ads UI.

---

## 🎯 Next Steps - Phase 3

Phase 3 will implement:
- ✨ `update_campaign_budget()` - Update existing budgets
- ✨ `set_target_roas()` - Update ROAS targets
- ✨ Budget adjustment types (INCREASE_BY_PERCENT, etc.)
- ✨ Get current budget before adjustment
- ✨ Integration tests

---

## 📝 Code Quality

### Metrics:
- **Lines of Code:** 410 (mutate/pmax.py)
- **Test Coverage:** 14 tests, all passing
- **Documentation:** Comprehensive docstrings
- **Error Handling:** Try/catch in all API calls
- **Logging:** INFO/DEBUG/ERROR levels

### Code Style:
- ✅ Type hints for all parameters
- ✅ Docstrings for all functions
- ✅ PEP 8 compliant
- ✅ Clear variable names
- ✅ Modular design

---

## ✅ Phase 2 Checklist

| Task | Status |
|------|--------|
| Create PerformanceMaxCampaign class | ✅ |
| Implement budget creation | ✅ |
| Implement campaign creation | ✅ |
| Implement asset group creation | ✅ |
| Implement Merchant Center linking | ✅ |
| Integrate with MCP tool | ✅ |
| Write unit tests (14+) | ✅ |
| Error handling | ✅ |
| Documentation | ✅ |
| All tests passing (57/57) | ✅ |

**Phase 2 Complete!** 🎉

Ready for Phase 3: Budget & ROAS Management 🚀

---

## 🔗 Resources

### Google Ads API Docs:
- [Performance Max Campaigns](https://developers.google.com/google-ads/api/docs/performance-max/overview)
- [Campaign Budgets](https://developers.google.com/google-ads/api/reference/rpc/v19/CampaignBudget)
- [Asset Groups](https://developers.google.com/google-ads/api/reference/rpc/v19/AssetGroup)
- [Shopping Settings](https://developers.google.com/google-ads/api/reference/rpc/v19/ShoppingSetting)

### Project Files:
- `mutate/pmax.py` - Implementation
- `tests/test_pmax.py` - Tests
- `google_ads_server.py` - MCP integration
- `schemas/create_pmax.json` - JSON Schema

---

**Built with ❤️ for huge8888/mcp-google-ads**
