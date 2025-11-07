# Safe Rollout Checklist

Complete checklist for safely deploying the Google Ads MCP Agent to production.

## Pre-Deployment Checklist

### 1. Environment Configuration

- [ ] **Create `.env` file** from `.env.example`
  ```bash
  cp .env.example .env
  ```

- [ ] **Set authentication method**
  ```bash
  # For OAuth2 (recommended for development)
  GOOGLE_ADS_AUTH_TYPE=oauth
  GOOGLE_ADS_CLIENT_SECRET_PATH=/path/to/client_secret.json
  GOOGLE_ADS_TOKEN_PATH=/path/to/token.pickle

  # For Service Account (recommended for production)
  GOOGLE_ADS_AUTH_TYPE=service_account
  GOOGLE_ADS_SERVICE_ACCOUNT_PATH=/path/to/service_account.json
  GOOGLE_ADS_IMPERSONATE_EMAIL=user@example.com
  ```

- [ ] **Configure guardrails** (optional, recommended for production)
  ```bash
  # Enable dry-run mode for initial testing
  DRY_RUN=true

  # Require confirmation for bulk operations
  REQUIRE_CONFIRMATION=true

  # Set maximum budget limit (in micros, default: $100,000)
  MAX_BUDGET_MICROS=100000000000

  # Set maximum campaigns for bulk operations (default: 50)
  MAX_CAMPAIGNS_BULK=50
  ```

- [ ] **Set Google Ads account**
  ```bash
  GOOGLE_ADS_LOGIN_CUSTOMER_ID=1234567890
  GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
  ```

### 2. Dependency Installation

- [ ] **Create virtual environment**
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  ```

- [ ] **Install dependencies**
  ```bash
  pip install -r requirements.txt
  ```

- [ ] **Verify installation**
  ```bash
  make check-env
  ```

### 3. Testing

- [ ] **Run all tests**
  ```bash
  make test
  ```

- [ ] **Expected results:**
  - All core tests passing (60+)
  - Only expected failures (async tests, OAuth browser tests)

- [ ] **Test dry-run mode**
  ```bash
  DRY_RUN=true python google_ads_server.py
  ```

### 4. Authentication Setup

- [ ] **OAuth2 Setup** (if using OAuth)
  1. Create OAuth2 credentials in Google Cloud Console
  2. Download `client_secret.json`
  3. Run authentication flow:
     ```bash
     python google_ads_server.py
     # Follow browser prompt to authorize
     ```
  4. Verify `token.pickle` created

- [ ] **Service Account Setup** (if using service account)
  1. Create service account in Google Cloud Console
  2. Download service account JSON
  3. Grant access in Google Ads account (Admin > Access & security > Users)
  4. Test authentication:
     ```bash
     python check_setup.py
     ```

### 5. Google Merchant Center Setup (if using GMC features)

- [ ] **Link GMC account to Google Ads**
  - In Google Ads: Tools > Linked accounts > Google Merchant Center

- [ ] **Verify merchant_center_id**
  - Note your GMC account ID (9 digits)

- [ ] **Test GMC MCP server** (optional)
  ```bash
  python mcp-gmc/gmc_server.py
  ```

---

## Initial Testing Phase

### Phase 1: Dry-Run Testing (1-2 days)

- [ ] **Enable dry-run mode**
  ```bash
  DRY_RUN=true
  ```

- [ ] **Test all operations in dry-run mode**
  - [ ] Create campaign (dry-run)
  - [ ] Update budget (dry-run)
  - [ ] Set ROAS (dry-run)
  - [ ] Pause/enable campaign (dry-run)
  - [ ] Run GAQL queries

- [ ] **Verify dry-run responses**
  - Check for `"dry_run": true` in responses
  - Verify `"would_execute"` field
  - Review any warnings

### Phase 2: Read-Only Testing (2-3 days)

- [ ] **Disable dry-run mode**
  ```bash
  DRY_RUN=false
  ```

- [ ] **Test read-only operations**
  - [ ] Run GAQL queries (Performance Max 7 days)
  - [ ] List campaigns
  - [ ] Get budget info
  - [ ] Get bidding strategy

- [ ] **Verify responses**
  - Check data accuracy
  - Verify customer IDs
  - Check metrics values

### Phase 3: Low-Impact Testing (3-5 days)

- [ ] **Test on a test campaign only**
  - Create a new campaign with minimal budget ($1-5/day)
  - Use PAUSED status initially

- [ ] **Test operations**
  - [ ] Create campaign (PAUSED)
  - [ ] Verify campaign created in Google Ads UI
  - [ ] Update budget (small amount)
  - [ ] Verify budget updated in UI
  - [ ] Enable campaign
  - [ ] Monitor for 24 hours
  - [ ] Pause campaign
  - [ ] Delete campaign

### Phase 4: Production Pilot (1 week)

- [ ] **Select pilot campaigns**
  - Choose 2-3 non-critical campaigns
  - Campaigns with existing performance data

- [ ] **Gradual rollout**
  - [ ] Day 1-2: Monitor only (GAQL queries)
  - [ ] Day 3-4: Budget adjustments only
  - [ ] Day 5-6: ROAS adjustments
  - [ ] Day 7: Full automation (if successful)

- [ ] **Monitor metrics**
  - [ ] No unexpected spend
  - [ ] ROAS targets maintained
  - [ ] No campaign disruptions
  - [ ] API error rates < 1%

---

## Production Deployment

### Security Checklist

- [ ] **Credentials Security**
  - [ ] `.env` file in `.gitignore`
  - [ ] `token.pickle` in `.gitignore`
  - [ ] Service account JSON in `.gitignore`
  - [ ] No credentials in code
  - [ ] No credentials in logs

- [ ] **Access Control**
  - [ ] Limit access to production credentials
  - [ ] Use service account for production (not OAuth)
  - [ ] Grant minimum necessary permissions in Google Ads
  - [ ] Enable 2FA for Google accounts

- [ ] **Logging and Monitoring**
  - [ ] Configure logging level (INFO for production)
  - [ ] Set up log aggregation (if applicable)
  - [ ] Monitor API quota usage
  - [ ] Set up alerts for errors

### Guardrails Configuration

- [ ] **Set appropriate limits**
  ```bash
  # Conservative limits for initial rollout
  MAX_BUDGET_MICROS=50000000000  # $50,000 max budget
  MAX_CAMPAIGNS_BULK=10          # Max 10 campaigns in bulk ops
  REQUIRE_CONFIRMATION=true      # Always require confirmation
  ```

- [ ] **Test guardrails**
  - [ ] Try to exceed budget limit (should fail)
  - [ ] Try bulk operation without confirmation (should fail)
  - [ ] Verify error messages are clear

### Monitoring Setup

- [ ] **Set up monitoring dashboards**
  - API call volume
  - Error rates
  - Budget changes
  - Campaign status changes

- [ ] **Configure alerts**
  - Budget exceeds threshold
  - Error rate > 5%
  - Unexpected campaign pauses
  - API quota warnings

- [ ] **Daily review process**
  - Review yesterday's operations
  - Check for anomalies
  - Verify spend is expected
  - Review error logs

---

## Operational Procedures

### Daily Operations

1. **Morning Check** (5 minutes)
   - [ ] Run budget pacing query (Recipe 5)
   - [ ] Check for campaigns with issues (Recipe 16)
   - [ ] Review error logs from previous day

2. **Budget Adjustments** (as needed)
   - [ ] Use `update_campaign_budget` tool
   - [ ] Verify change in Google Ads UI
   - [ ] Document reason for change

3. **Performance Review** (weekly)
   - [ ] Run PMax performance query (Recipe 1)
   - [ ] Compare to targets
   - [ ] Adjust ROAS if needed

### Incident Response

**Budget Overrun:**
1. Immediately pause affected campaigns
2. Investigate root cause
3. Adjust budgets if needed
4. Document incident

**ROAS Below Target:**
1. Review campaign performance (Recipe 4)
2. Check product performance (Recipe 10)
3. Adjust ROAS or pause campaign
4. Analyze causes (device, geo, etc.)

**API Errors:**
1. Check error message in logs
2. Verify credentials are valid
3. Check API quota status
4. Retry with exponential backoff

---

## Emergency Procedures

### Emergency Stop

If something goes wrong:

```bash
# 1. Enable dry-run mode immediately
export DRY_RUN=true

# 2. Pause all campaigns via UI or API
# Use pause_campaign tool with pattern:
# await pause_campaign(account_id="XXX", campaign_name_pattern="*", confirm=true)

# 3. Investigate issues
# Check logs, verify budgets, review changes

# 4. Resume gradually
# Re-enable one campaign at a time
# Monitor each for 24 hours before next
```

### Rollback Procedure

1. **Identify changes to rollback**
   - Review operation logs
   - Note campaign IDs affected

2. **Revert budgets**
   ```python
   # If budget was increased
   await update_campaign_budget(
       account_id="XXX",
       campaign_id="YYY",
       new_amount_micros=previous_budget_micros
   )
   ```

3. **Revert ROAS**
   ```python
   await set_target_roas(
       account_id="XXX",
       campaign_id="YYY",
       target_roas=previous_roas
   )
   ```

4. **Pause campaigns if needed**
   ```python
   await pause_campaign(
       account_id="XXX",
       campaign_id="YYY"
   )
   ```

---

## Success Criteria

After 2 weeks of production use, verify:

- [ ] **Reliability**
  - [ ] 99%+ API call success rate
  - [ ] No unexpected budget overruns
  - [ ] No campaign disruptions

- [ ] **Performance**
  - [ ] ROAS targets maintained or improved
  - [ ] Budget pacing within 10% of target
  - [ ] No degradation in campaign performance

- [ ] **Operational**
  - [ ] Team is comfortable using tools
  - [ ] Error handling is effective
  - [ ] Monitoring is adequate
  - [ ] Documentation is sufficient

---

## Post-Deployment

### Week 1 Review

- [ ] Review all operations performed
- [ ] Check for any issues or errors
- [ ] Gather team feedback
- [ ] Update documentation if needed

### Week 2-4: Optimization

- [ ] Identify automation opportunities
- [ ] Refine guardrail limits based on usage
- [ ] Add new GAQL recipes for specific needs
- [ ] Train team on advanced features

### Monthly Review

- [ ] Review API quota usage
- [ ] Analyze cost savings from automation
- [ ] Update procedures based on learnings
- [ ] Plan new features or improvements

---

## Troubleshooting

### Common Issues

**Issue:** Authentication fails
- **Solution:** Delete `token.pickle`, re-authenticate

**Issue:** Budget updates don't appear in UI
- **Solution:** Wait 5 minutes for API sync, refresh UI

**Issue:** Dry-run mode not working
- **Solution:** Verify `DRY_RUN=true` in environment

**Issue:** Bulk operation fails
- **Solution:** Check `confirm=true` is set

**Issue:** GAQL query returns no results
- **Solution:** Check date filter, verify campaigns exist

---

## Support and Resources

### Documentation
- `README.md` - Main documentation
- `docs/GAQL_RECIPES.md` - Query recipes
- `mcp-gmc/README.md` - GMC documentation
- `PHASE*_COMPLETE.md` - Phase documentation

### Testing
```bash
make test         # Run all tests
make check-env    # Verify environment
make clean        # Clean up
```

### Logs
```bash
# View logs
tail -f logs/google_ads_mcp.log

# Search for errors
grep ERROR logs/google_ads_mcp.log
```

---

## Sign-Off

### Pre-Production Sign-Off

- [ ] Technical Lead approval
- [ ] Security review completed
- [ ] Testing phase completed successfully
- [ ] Documentation reviewed and approved
- [ ] Team trained on tools and procedures

**Signed:** _________________ **Date:** _________

### Production Deployment Sign-Off

- [ ] Pilot phase completed successfully
- [ ] Monitoring configured
- [ ] Emergency procedures tested
- [ ] Stakeholders notified

**Signed:** _________________ **Date:** _________

---

**Remember:** When in doubt, enable `DRY_RUN=true` and test first!
