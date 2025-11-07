# ✅ Phase 7 Complete - Guardrails & Safety Systems

## 🚀 Phase 7 Summary

Phase 7 adds **comprehensive guardrails and safety systems** for production use!

### สิ่งที่ทำเสร็จ:

1. ✅ **Guardrail System** (`mutate/guardrails.py`)
   - Dry-run mode for safe testing
   - Budget validation
   - ROAS validation
   - Bulk operation limits
   - Sensitive data masking

2. ✅ **CI/CD Pipeline** (`.github/workflows/ci.yml`)
   - Automated testing with pytest
   - Code quality checks (flake8, black, isort)
   - Security scanning (bandit, safety)
   - Guardrail validation tests

3. ✅ **Safe Rollout Checklist** (`docs/SAFE_ROLLOUT_CHECKLIST.md`)
   - Pre-deployment checklist
   - Testing phases
   - Production deployment guide
   - Emergency procedures
   - Monitoring setup

4. ✅ **Environment Configuration**
   - Updated `.env.example` with guardrail settings
   - Documented all safety parameters

---

## 📦 New Files & Updates

### Files Created:
```
mutate/guardrails.py                   # Guardrail system (300+ lines)
.github/workflows/ci.yml               # CI/CD pipeline
docs/SAFE_ROLLOUT_CHECKLIST.md        # Safe deployment guide
PHASE7_COMPLETE.md                     # This file
```

### Files Updated:
```
.env.example                           # Added guardrail settings
```

---

## 🎯 Guardrail Features

### 1. Dry-Run Mode

**Purpose:** Test operations without making actual API changes

**Configuration:**
```bash
# Enable dry-run mode
DRY_RUN=true
```

**Usage:**
```python
from mutate.guardrails import is_dry_run

if is_dry_run():
    print("Running in dry-run mode - no actual changes will be made")
```

**Decorator Support:**
```python
from mutate.guardrails import dry_run

@dry_run("create_campaign")
def create_campaign(...):
    # Function implementation
    pass
```

**Dry-Run Response:**
```json
{
  "dry_run": true,
  "operation": "create_campaign",
  "would_execute": true,
  "params": {
    "campaign_name": "Test Campaign",
    "account_id": "******7890"
  },
  "warnings": [],
  "message": "This is a DRY RUN. No actual changes were made."
}
```

---

### 2. Budget Validation

**Purpose:** Prevent budgets exceeding safe limits

**Configuration:**
```bash
# Maximum budget in micros (default: $100,000)
MAX_BUDGET_MICROS=100000000000
```

**Validation:**
```python
from mutate.guardrails import validate_budget_amount, GuardrailViolation

try:
    validate_budget_amount(150_000_000_000)  # $150,000
except GuardrailViolation as e:
    print(f"Budget rejected: {e}")
    # Output: "Budget 150000.00 exceeds maximum 100000.00"
```

**Features:**
- Prevents negative budgets
- Enforces maximum budget limit
- Configurable via environment variable
- Clear error messages

---

### 3. ROAS Validation

**Purpose:** Ensure ROAS targets are reasonable

**Validation:**
```python
from mutate.guardrails import validate_roas, GuardrailViolation

# Valid ROAS (0.01 - 100)
validate_roas(2.5)  # ✅ OK

# Invalid ROAS
try:
    validate_roas(150)  # Too high
except GuardrailViolation:
    print("ROAS rejected")

try:
    validate_roas(0.001)  # Too low
except GuardrailViolation:
    print("ROAS rejected")
```

**Limits:**
- Minimum: 0.01 (1% ROAS)
- Maximum: 100 (10,000% ROAS)

---

### 4. Bulk Operation Limits

**Purpose:** Prevent accidental mass changes

**Configuration:**
```bash
# Maximum campaigns in bulk operations (default: 50)
MAX_CAMPAIGNS_BULK=50

# Require confirmation for bulk operations
REQUIRE_CONFIRMATION=true
```

**Validation:**
```python
from mutate.guardrails import validate_bulk_operation, check_confirmation_required

# Check campaign count
validate_bulk_operation(100, "pause_campaigns")
# Raises: GuardrailViolation - exceeds maximum 50

# Check confirmation
check_confirmation_required("pause_campaigns", confirm=False, affected_count=10)
# Raises: GuardrailViolation - confirmation required
```

**Features:**
- Limits number of campaigns affected
- Requires explicit confirmation
- Prevents accidental bulk operations

---

### 5. Sensitive Data Masking

**Purpose:** Protect sensitive data in logs and responses

**Usage:**
```python
from mutate.guardrails import mask_sensitive_logs

log_message = "Processing customer 1234567890 with token abc123..."
masked = mask_sensitive_logs(log_message)
# Output: "Processing customer 123456**** with token ****..."
```

**What Gets Masked:**
- Customer IDs (show last 4 digits only)
- Access tokens (complete masking)
- Authorization headers (complete masking)
- Account IDs (show last 4 digits only)

**Automatic Masking in Dry-Run:**
```python
result = DryRunResult(
    operation="create_campaign",
    params={"account_id": "1234567890"}
)
# Automatically masked in response: "account_id": "******7890"
```

---

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

**Triggers:**
- Push to `main`, `develop`, `claude/**` branches
- Pull requests to `main`, `develop`

**Jobs:**

#### 1. Test Job
```yaml
- Python 3.11 and 3.12
- Run pytest with verbose output
- Generate coverage report (Python 3.11)
- Upload coverage artifacts
```

#### 2. Lint Job
```yaml
- Run flake8 (syntax errors and code quality)
- Check code formatting with black
- Verify import sorting with isort
```

#### 3. Security Job
```yaml
- Run bandit security scanner
- Check dependencies for vulnerabilities (safety)
- Upload security reports
```

#### 4. Guardrails Job
```yaml
- Test dry-run mode
- Verify guardrail configuration
- Test budget validation
```

#### 5. Build Job
```yaml
- Verify all imports work
- Check .env.example exists
- Verify README exists
```

**Example Workflow Run:**
```
✅ Test (Python 3.11) - 60 tests passed
✅ Test (Python 3.12) - 60 tests passed
✅ Lint - No issues found
✅ Security - No critical vulnerabilities
✅ Guardrails - All checks passed
✅ Build - All imports OK
```

---

## 📋 Safe Rollout Process

### Phase 1: Dry-Run Testing (1-2 days)

```bash
# Step 1: Enable dry-run mode
export DRY_RUN=true

# Step 2: Test all operations
# All operations return dry-run responses, no actual changes made

# Step 3: Verify responses
# Check for "dry_run": true and "would_execute" fields
```

### Phase 2: Read-Only Testing (2-3 days)

```bash
# Step 1: Disable dry-run mode
export DRY_RUN=false

# Step 2: Test read-only operations only
# - GAQL queries
# - List campaigns
# - Get budget/bidding info

# No write operations yet
```

### Phase 3: Low-Impact Testing (3-5 days)

```bash
# Create test campaign with minimal budget
await create_pmax_campaign(
    account_id="XXX",
    campaign_name="TEST - Do Not Edit",
    daily_budget_currency=1,  # $1/day
    status="PAUSED"
)

# Test operations on test campaign only
# - Update budget
# - Set ROAS
# - Enable/pause
# - Monitor for 24 hours
```

### Phase 4: Production Pilot (1 week)

```bash
# Select 2-3 non-critical campaigns
# Gradual rollout:
# - Day 1-2: Monitor only
# - Day 3-4: Budget adjustments
# - Day 5-6: ROAS adjustments
# - Day 7: Full automation (if successful)
```

---

## 🔒 Emergency Procedures

### Emergency Stop

```bash
# 1. Enable dry-run mode immediately
export DRY_RUN=true

# 2. Pause all campaigns (via pattern)
await pause_campaign(
    account_id="XXX",
    campaign_name_pattern="*",
    confirm=true
)

# 3. Investigate issues
# - Check logs
# - Verify budgets
# - Review recent changes

# 4. Resume gradually
# - Re-enable one campaign at a time
# - Monitor each for 24 hours
```

### Rollback Procedure

```python
# 1. Identify changes to rollback
# Review operation logs

# 2. Revert budgets
await update_campaign_budget(
    account_id="XXX",
    campaign_id="YYY",
    new_amount_micros=previous_budget_micros
)

# 3. Revert ROAS
await set_target_roas(
    account_id="XXX",
    campaign_id="YYY",
    target_roas=previous_roas
)

# 4. Pause campaigns if needed
await pause_campaign(
    account_id="XXX",
    campaign_id="YYY"
)
```

---

## 💡 Best Practices

### 1. Always Test in Dry-Run First

```bash
# Before any major operation
DRY_RUN=true

# Test the operation
# Review the dry-run response
# Verify "would_execute": true

# Then disable dry-run
DRY_RUN=false

# Execute for real
```

### 2. Use Conservative Limits Initially

```bash
# Start with low limits
MAX_BUDGET_MICROS=50000000000    # $50,000
MAX_CAMPAIGNS_BULK=10            # 10 campaigns

# Increase gradually based on comfort level
```

### 3. Monitor Everything

```bash
# Daily checks
- Budget pacing (Recipe 5)
- Campaign issues (Recipe 16)
- Error logs

# Weekly reviews
- Performance vs targets (Recipe 4)
- API quota usage
- Operation logs
```

### 4. Document All Changes

```
# Keep a changelog
- Date: 2025-11-07
- Operation: Updated budget
- Campaign: SEW | Sunglasses PMax
- Old value: $1,000/day
- New value: $1,500/day
- Reason: Scaling successful campaign
- Result: ROAS maintained at 2.8
```

---

## 🧪 Testing Guardrails

### Test Budget Validation

```python
from mutate.guardrails import validate_budget_amount, GuardrailViolation

# Test 1: Valid budget
try:
    validate_budget_amount(50_000_000_000)  # $50,000
    print("✅ Valid budget accepted")
except GuardrailViolation:
    print("❌ Unexpected rejection")

# Test 2: Excessive budget
try:
    validate_budget_amount(200_000_000_000)  # $200,000
    print("❌ Excessive budget accepted")
except GuardrailViolation as e:
    print(f"✅ Excessive budget rejected: {e}")

# Test 3: Negative budget
try:
    validate_budget_amount(-1000)
    print("❌ Negative budget accepted")
except GuardrailViolation as e:
    print(f"✅ Negative budget rejected: {e}")
```

### Test Dry-Run Mode

```bash
# Set dry-run mode
export DRY_RUN=true

# Run any operation
python -c "
from mutate.guardrails import is_dry_run
assert is_dry_run() == True
print('✅ Dry-run mode enabled')
"
```

### Test Bulk Operation Limits

```python
from mutate.guardrails import validate_bulk_operation

# Test within limit
validate_bulk_operation(10, "test_operation")  # ✅ OK

# Test exceeding limit
try:
    validate_bulk_operation(100, "test_operation")
except GuardrailViolation as e:
    print(f"✅ Bulk limit enforced: {e}")
```

---

## 📊 Guardrail Configuration

### View Current Configuration

```python
from mutate.guardrails import get_guardrail_config
import json

config = get_guardrail_config()
print(json.dumps(config, indent=2))
```

**Example Output:**
```json
{
  "dry_run_enabled": false,
  "require_confirmation": true,
  "max_budget_micros": 100000000000,
  "max_budget_currency": 100000.0,
  "max_campaigns_bulk": 50,
  "environment_variables": {
    "DRY_RUN": "false",
    "REQUIRE_CONFIRMATION": "true",
    "MAX_BUDGET_MICROS": "100000000000",
    "MAX_CAMPAIGNS_BULK": "50"
  }
}
```

---

## ✅ Phase 7 Checklist

| Task | Status |
|------|--------|
| Create guardrail system | ✅ |
| Implement dry-run mode | ✅ |
| Budget validation | ✅ |
| ROAS validation | ✅ |
| Bulk operation limits | ✅ |
| Sensitive data masking | ✅ |
| Guardrail decorator | ✅ |
| CI/CD pipeline setup | ✅ |
| Automated testing | ✅ |
| Code quality checks | ✅ |
| Security scanning | ✅ |
| Safe rollout checklist | ✅ |
| Emergency procedures | ✅ |
| Update .env.example | ✅ |

**Phase 7 Complete!** 🎉

Ready for Phase 8: Real-World Usage Prompts and Examples 🚀

---

## 🔗 Resources

### Documentation
- `mutate/guardrails.py` - Guardrail system implementation
- `.github/workflows/ci.yml` - CI/CD pipeline
- `docs/SAFE_ROLLOUT_CHECKLIST.md` - Safe deployment guide
- `.env.example` - Environment configuration with guardrails

### Testing
```bash
# Run all tests
make test

# Run with coverage
pytest tests/ --cov=mutate --cov-report=html

# Run security scan
bandit -r . -ll
```

### Monitoring
```bash
# View guardrail configuration
python -c "from mutate.guardrails import get_guardrail_config; import json; print(json.dumps(get_guardrail_config(), indent=2))"

# Test dry-run mode
DRY_RUN=true python -c "from mutate.guardrails import is_dry_run; print(f'Dry-run: {is_dry_run()}')"
```

---

**Built with ❤️ for huge8888/mcp-google-ads**

**Safety First!** 🛡️
