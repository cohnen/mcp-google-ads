# ✅ Phase 1 Complete - Schema และ Stub Tools สำหรับ Mutate Operations

## 📦 สิ่งที่เพิ่มใน Phase 1

### 1. JSON Schemas (6 files)
สร้างโฟลเดอร์ `schemas/` พร้อม validation schemas:

```
schemas/
├── __init__.py              # Schema loader และ validation utilities
├── create_pmax.json         # สร้าง Performance Max campaign
├── update_budget.json       # อัพเดตงบ campaign
├── set_target_roas.json     # ตั้งค่า target ROAS
├── pause_campaign.json      # หยุด campaign
├── enable_campaign.json     # เปิดใช้ campaign
└── attach_merchant_center.json  # เชื่อม Merchant Center
```

#### Schema Features:
- ✅ JSON Schema Draft 7 compliant
- ✅ รองรับ validation ด้วย `jsonschema` library
- ✅ มี examples ในทุก property
- ✅ รองรับทั้ง micros และ currency units
- ✅ Pattern validation สำหรับ IDs, dates, country codes
- ✅ oneOf/anyOf สำหรับ alternative parameters

### 2. Utility Functions
สร้างโฟลเดอร์ `mutate/` พร้อม helper functions:

```
mutate/
├── __init__.py          # Module exports
└── utils.py             # Utility functions
```

#### Available Utils:
- `format_customer_id()` - Format customer ID to 10 digits
- `micros_to_currency()` - Convert micros to currency
- `currency_to_micros()` - Convert currency to micros
- `validate_date_format()` - Validate YYYY-MM-DD format
- `build_campaign_resource_name()` - Build resource names
- `parse_resource_name()` - Parse resource names
- `sanitize_campaign_name()` - Sanitize campaign names

### 3. Unit Tests (43 tests, all passing ✅)
สร้างโฟลเดอร์ `tests/` พร้อม comprehensive tests:

```
tests/
├── __init__.py
├── test_schemas.py      # Schema validation tests (24 tests)
└── test_utils.py        # Utility function tests (19 tests)
```

#### Test Coverage:
```
tests/test_schemas.py::TestSchemaLoading - 5 tests ✅
tests/test_schemas.py::TestCreatePMaxSchema - 6 tests ✅
tests/test_schemas.py::TestUpdateBudgetSchema - 3 tests ✅
tests/test_schemas.py::TestSetTargetROASSchema - 3 tests ✅
tests/test_schemas.py::TestPauseCampaignSchema - 3 tests ✅
tests/test_schemas.py::TestEnableCampaignSchema - 1 test ✅
tests/test_schemas.py::TestAttachMerchantCenterSchema - 3 tests ✅

tests/test_utils.py::TestFormatCustomerId - 5 tests ✅
tests/test_utils.py::TestCurrencyConversion - 3 tests ✅
tests/test_utils.py::TestDateValidation - 2 tests ✅
tests/test_utils.py::TestResourceNames - 4 tests ✅
tests/test_utils.py::TestCampaignNameSanitization - 5 tests ✅

========================
43 passed in 0.21s ✅
========================
```

### 4. MCP Tool Stubs (6 new tools)
เพิ่ม stub implementations ใน `google_ads_server.py`:

#### New Tools Available:
1. **`create_pmax_campaign`**
   - สร้าง Performance Max campaign ใหม่
   - รองรับ budget, ROAS, Merchant Center, targeting
   - Status: Stub (จะ implement จริงใน Phase 2)

2. **`update_campaign_budget`**
   - อัพเดตงบ campaign
   - รองรับ SET, INCREASE_BY_PERCENT, DECREASE_BY_PERCENT
   - Status: Stub (จะ implement ใน Phase 3)

3. **`set_target_roas`**
   - ตั้งค่า target ROAS bidding strategy
   - รองรับ bid ceiling และ floor
   - Status: Stub (จะ implement ใน Phase 3)

4. **`pause_campaign`**
   - หยุด campaign (single หรือ bulk)
   - รองรับ pattern matching
   - Status: Stub (จะ implement ใน Phase 4)

5. **`enable_campaign`**
   - เปิดใช้ campaign
   - มี safety checks
   - Status: Stub (จะ implement ใน Phase 4)

6. **`attach_merchant_center`**
   - เชื่อม Merchant Center feed กับ PMax campaign
   - รองรับ feed labels
   - Status: Stub (จะ implement ใน Phase 4)

## 🧪 การทดสอบ

### รัน Unit Tests
```bash
# รัน tests ทั้งหมด
make test

# หรือ
.venv/bin/python -m pytest tests/ -v

# รันเฉพาะ schema tests
.venv/bin/python -m pytest tests/test_schemas.py -v

# รันเฉพาะ utils tests
.venv/bin/python -m pytest tests/test_utils.py -v
```

### ทดสอบ Schema Validation
```python
from schemas import load_schema, validate_params

# ตัวอย่างการ validate
params = {
    "account_id": "1234567890",
    "campaign_name": "Test Campaign",
    "daily_budget_currency": 1500
}

is_valid, error = validate_params('create_pmax', params)
if is_valid:
    print("✅ Valid!")
else:
    print(f"❌ Invalid: {error}")
```

### ทดสอบ Stub Tools
```bash
# รัน MCP server
make run

# Tools จะ return stub responses:
# {
#   "status": "stub",
#   "message": "create_pmax_campaign will be implemented in Phase 2",
#   "requested_params": {...}
# }
```

## 📊 โครงสร้างไฟล์ใหม่

```
mcp-google-ads/
├── schemas/                    # ✨ NEW
│   ├── __init__.py
│   ├── create_pmax.json
│   ├── update_budget.json
│   ├── set_target_roas.json
│   ├── pause_campaign.json
│   ├── enable_campaign.json
│   └── attach_merchant_center.json
├── mutate/                     # ✨ NEW
│   ├── __init__.py
│   └── utils.py
├── tests/                      # ✨ NEW
│   ├── __init__.py
│   ├── test_schemas.py
│   └── test_utils.py
├── google_ads_server.py        # ✏️ UPDATED (6 new tools)
├── requirements.txt            # ✏️ UPDATED (pytest, jsonschema)
└── ...
```

## 🎯 Schema Examples

### Create PMax Campaign
```json
{
  "account_id": "1234567890",
  "campaign_name": "SEW | Sunglasses PMax | TH | 2025-11",
  "daily_budget_currency": 1500,
  "target_roas": 2.5,
  "merchant_center_id": "123456789",
  "feed_label": "promo_nov2025",
  "start_date": "2025-11-10",
  "status": "PAUSED",
  "country_codes": ["TH"],
  "language_codes": ["th"]
}
```

### Update Budget
```json
{
  "account_id": "1234567890",
  "campaign_id": "9876543210",
  "adjustment_type": "INCREASE_BY_PERCENT",
  "adjustment_value": 20
}
```

### Set Target ROAS
```json
{
  "account_id": "1234567890",
  "campaign_id": "9876543210",
  "target_roas": 3.0,
  "cpc_bid_ceiling_micros": 5000000
}
```

### Attach Merchant Center
```json
{
  "account_id": "1234567890",
  "campaign_id": "9876543210",
  "merchant_center_id": "123456789",
  "feed_label": "promo_nov2025",
  "sales_country": "TH",
  "language_code": "th"
}
```

## 🔧 ฟีเจอร์เด่น

### 1. Flexible Budget Input
รองรับทั้ง micros และ currency units:
```python
# Option 1: ใช้ micros
{"daily_budget_micros": 1500000000}  # 1500 units

# Option 2: ใช้ currency (จะถูกแปลงเป็น micros อัตโนมัติ)
{"daily_budget_currency": 1500}      # 1500 THB/USD/etc
```

### 2. Resource Name Flexibility
รองรับทั้ง campaign_id และ full resource name:
```python
# Option 1: ใช้ campaign_id
{"campaign_id": "9876543210"}

# Option 2: ใช้ full resource name
{"campaign_resource_name": "customers/1234567890/campaigns/9876543210"}
```

### 3. Bulk Operations
รองรับการทำงานหลาย campaigns พร้อมกัน:
```python
# Single campaign
{"campaign_id": "9876543210"}

# Multiple campaigns
{"campaign_ids": ["9876543210", "9876543211", "9876543212"]}

# Pattern matching (ระวัง! ต้อง confirm=true)
{"campaign_name_pattern": "Test*", "confirm": true}
```

### 4. Safety Features
- ✅ Schema validation ก่อนส่งไป API
- ✅ Pattern matching ต้อง confirm
- ✅ Safety checks สำหรับ enable_campaign
- ✅ Input sanitization (campaign names, customer IDs)

## 🚀 Next Steps - Phase 2

Phase 2 จะ implement ฟังก์ชันจริงสำหรับ:
- ✨ `create_pmax_campaign()` - สร้าง PMax campaign ด้วย Google Ads API
- ✨ สร้าง Budget, Campaign, Asset Group
- ✨ ตั้งค่า targeting (countries, languages)
- ✨ รองรับ start_date, end_date
- ✨ Integration tests

## 📝 Dependencies Added

```txt
# Testing (new)
pytest>=8.0.0
jsonschema>=4.20.0
```

## 🎓 การใช้งาน Schema Module

```python
from schemas import (
    load_schema,
    validate_params,
    list_available_schemas,
    get_required_fields,
    get_schema_examples
)

# ดูว่ามี schema อะไรบ้าง
schemas = list_available_schemas()
# ['create_pmax', 'update_budget', 'set_target_roas', ...]

# ดู required fields
required = get_required_fields('create_pmax')
# ['account_id', 'campaign_name']

# ดู examples
examples = get_schema_examples('create_pmax')
# {'account_id': '1234567890', 'campaign_name': 'Example', ...}

# Validate parameters
params = {"account_id": "1234567890", ...}
is_valid, error = validate_params('create_pmax', params)
```

## ✅ Phase 1 Summary

| Item | Status | Count |
|------|--------|-------|
| JSON Schemas | ✅ | 6 |
| Utility Functions | ✅ | 7 |
| Unit Tests | ✅ | 43/43 passing |
| MCP Tool Stubs | ✅ | 6 |
| Documentation | ✅ | Complete |

**Phase 1 เสร็จสมบูรณ์!** 🎉

พร้อมสำหรับ Phase 2: Implementation ของ create_pmax_campaign()

---

## 🔍 Validation Examples

### Valid Examples

#### ✅ Minimal params
```python
{
  "account_id": "1234567890",
  "campaign_name": "Test",
  "daily_budget_micros": 1500000000
}
# Result: Valid ✅
```

#### ✅ With currency instead of micros
```python
{
  "account_id": "1234567890",
  "campaign_name": "Test",
  "daily_budget_currency": 1500
}
# Result: Valid ✅
```

#### ✅ Full configuration
```python
{
  "account_id": "1234567890",
  "campaign_name": "SEW | Sunglasses | TH",
  "daily_budget_currency": 1500,
  "target_roas": 2.5,
  "merchant_center_id": "123456789",
  "feed_label": "promo",
  "start_date": "2025-11-10",
  "country_codes": ["TH"],
  "language_codes": ["th"]
}
# Result: Valid ✅
```

### Invalid Examples

#### ❌ Invalid account_id format
```python
{
  "account_id": "123",  # Too short
  "campaign_name": "Test",
  "daily_budget_micros": 1500000000
}
# Error: account_id must match pattern ^[0-9]{10}$
```

#### ❌ Missing required field
```python
{
  "account_id": "1234567890",
  # Missing campaign_name
  "daily_budget_micros": 1500000000
}
# Error: 'campaign_name' is a required property
```

#### ❌ Invalid date format
```python
{
  "account_id": "1234567890",
  "campaign_name": "Test",
  "daily_budget_currency": 1500,
  "start_date": "2025/11/10"  # Wrong format
}
# Error: start_date must match pattern YYYY-MM-DD
```

---

**Next:** Phase 2 - Implement `create_pmax_campaign()` 🚀
