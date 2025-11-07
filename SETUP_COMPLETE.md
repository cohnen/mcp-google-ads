# ✅ MCP Google Ads Agent - Phase 0 Setup Complete

## 📦 สิ่งที่ติดตั้งเสร็จแล้ว

### 1. Virtual Environment
- ✅ สร้าง `.venv` สำหรับ Python 3.11
- ✅ อัพเกรด pip เป็นเวอร์ชันล่าสุด (25.3)
- ✅ ติดตั้ง dependencies ครบถ้วน:
  - `mcp>=0.0.11` - Model Context Protocol
  - `google-auth>=2.25.2` - Google Authentication
  - `google-auth-oauthlib>=1.1.0` - OAuth support
  - `requests>=2.31.0` - HTTP client
  - `python-dotenv>=1.0.0` - Environment variables
  - `matplotlib>=3.7.3` - Data visualization
  - `pandas>=2.1.4` - Data analysis

### 2. Configuration Files
- ✅ สร้าง `.env` จาก `.env.example` พร้อมใช้งาน
- ✅ สร้าง `Makefile` สำหรับจัดการ project
- ✅ สร้าง `check_setup.py` สำหรับตรวจสอบ environment

### 3. Project Structure
```
mcp-google-ads/
├── .venv/                      # Virtual environment
├── .env                        # Environment variables (needs config)
├── .env.example                # Template
├── Makefile                    # Build automation
├── check_setup.py              # Setup verification
├── google_ads_server.py        # Main MCP server
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
└── test_*.py                   # Test files
```

## 🎯 Features ที่พร้อมใช้งาน

### MCP Tools (Read-Only)
โครงสร้างเดิมของ repo มี tools สำหรับอ่านข้อมูลจาก Google Ads:
- ✅ `list_accounts()` - แสดงรายการ accounts
- ✅ `execute_gaql_query()` - รัน GAQL queries
- ✅ `get_campaign_performance()` - ดูผล campaigns
- ✅ `get_ad_performance()` - ดูผล ads
- ✅ `run_gaql()` - รัน GAQL พร้อม format options
- ✅ `get_ad_creatives()` - ดู ad creatives
- ✅ `get_account_currency()` - ตรวจสอบ currency
- ✅ `get_image_assets()` - ดู image assets
- ✅ `download_image_asset()` - ดาวน์โหลด images
- ✅ `analyze_image_assets()` - วิเคราะห์ image performance

### Authentication Support
- ✅ OAuth 2.0 (User Authentication)
- ✅ Service Account (Server-to-Server)
- ✅ Automatic token refresh
- ✅ Environment-based configuration

## 📋 Makefile Commands

```bash
make help        # แสดงคำสั่งทั้งหมด
make setup       # ติดตั้ง environment ใหม่
make run         # รัน MCP server
make test        # รัน tests ด้วย pytest
make test-basic  # รัน basic functionality test
make test-auth   # ทดสอบ authentication
make check-env   # ตรวจสอบ environment
make version     # แสดง Python version และ packages
make clean       # ลบ venv และ cache files
```

## ⚙️ การใช้งานเบื้องต้น

### 1. ตรวจสอบ Setup
```bash
.venv/bin/python check_setup.py
```

### 2. Configure Credentials (ยังไม่จำเป็นสำหรับ Phase 1-8)
แก้ไขไฟล์ `.env`:
```bash
GOOGLE_ADS_AUTH_TYPE=oauth
GOOGLE_ADS_CREDENTIALS_PATH=/path/to/your/credentials.json
GOOGLE_ADS_DEVELOPER_TOKEN=your_actual_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=123-456-7890
```

### 3. รัน Server (ทดสอบ)
```bash
make run
# หรือ
.venv/bin/python google_ads_server.py
```

## 🚀 Next Steps - Phase 1-8

### Phase 1: เพิ่ม Schema สำหรับ MCP Tools (Mutate)
จะสร้าง JSON schemas สำหรับ:
- `create_pmax_campaign`
- `update_campaign_budget`
- `set_target_roas`
- `pause_campaign`
- `enable_campaign`
- `attach_merchant_center`

### Phase 2: ฟังก์ชันสร้าง Performance Max Campaign
- สร้าง `mutate/pmax.py`
- Implement create_pmax_campaign()
- รองรับ Budget, Asset Group, Merchant Center

### Phase 3: ฟังก์ชันปรับงบและ ROAS
- สร้าง `mutate/budgets.py` และ `mutate/bidding.py`
- Implement update_campaign_budget()
- Implement set_target_roas()

### Phase 4: การ Pause/Enable + Attach GMC
- สร้าง `mutate/status.py`
- Implement set_campaign_status()
- Implement attach_merchant_center()

### Phase 5: MCP สำหรับ Google Merchant Center
- สร้าง `mcp-gmc/gmc_server.py`
- Tools: upload_products, patch_price, patch_inventory

### Phase 6: GAQL Recipe
- สร้าง `docs/GAQL_RECIPES.md`
- เพิ่ม tool `run_gaql_recipe`

### Phase 7: Guardrail & Dry-Run
- Exception handler
- DRY_RUN mode
- GitHub Actions
- Safe rollout checklist

### Phase 8: Prompt Examples
- ตัวอย่างการใช้งานจริง
- Integration guide
- Best practices

## 📝 Notes

### Environment Variables ที่ต้องตั้งค่า (สำหรับใช้งานจริง)
```bash
# Required
GOOGLE_ADS_DEVELOPER_TOKEN=xxx
GOOGLE_ADS_CREDENTIALS_PATH=/path/to/credentials.json

# Optional
GOOGLE_ADS_LOGIN_CUSTOMER_ID=123-456-7890  # สำหรับ MCC accounts
GOOGLE_ADS_AUTH_TYPE=oauth                  # หรือ service_account
```

### สำหรับ Development
- Server จะรันได้แม้ไม่มี credentials
- Tools จะ return auth errors ซึ่งเป็นพฤติกรรมที่ถูกต้อง
- ใช้ DRY_RUN mode เพื่อทดสอบโดยไม่ยิง API จริง (Phase 7)

## 🔧 Troubleshooting

### ถ้า dependencies ติดตั้งไม่สำเร็จ
```bash
make clean
make setup
```

### ถ้า Python version ไม่ตรง
```bash
python3 --version  # ต้องเป็น 3.11+
```

### ถ้าต้องการ reinstall
```bash
rm -rf .venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 📊 Test Coverage

ปัจจุบันมี test files:
- `test_google_ads_mcp.py` - ทดสอบ MCP tools
- `test_token_refresh.py` - ทดสอบ authentication
- `format_customer_id_test.py` - ทดสอบ customer ID formatting

รัน tests:
```bash
make test          # รัน pytest
make test-basic    # รัน basic test
make test-auth     # ทดสอบ auth
```

---

## ✅ Phase 0 Summary

| Task | Status |
|------|--------|
| Create virtual environment | ✅ |
| Install dependencies | ✅ |
| Create .env file | ✅ |
| Create Makefile | ✅ |
| Verify dotenv loading | ✅ |
| Test basic functionality | ✅ |
| Document setup | ✅ |

**Phase 0 เสร็จสมบูรณ์!** 🎉

พร้อมสำหรับ Phase 1: เพิ่ม Schema สำหรับ MCP Tools (Mutate)
