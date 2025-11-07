"""
Unit tests for JSON schemas
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas import (
    load_schema,
    validate_params,
    list_available_schemas,
    get_required_fields,
    get_schema_examples,
)


class TestSchemaLoading:
    """Test schema loading functionality"""

    def test_list_available_schemas(self):
        """Test listing all available schemas"""
        schemas = list_available_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) > 0
        assert 'create_pmax' in schemas
        assert 'update_budget' in schemas
        assert 'set_target_roas' in schemas

    def test_load_valid_schema(self):
        """Test loading a valid schema"""
        schema = load_schema('create_pmax')
        assert isinstance(schema, dict)
        assert '$schema' in schema
        assert 'properties' in schema

    def test_load_invalid_schema(self):
        """Test loading an invalid schema name"""
        with pytest.raises(ValueError):
            load_schema('nonexistent_schema')

    def test_get_required_fields(self):
        """Test getting required fields from schema"""
        required = get_required_fields('create_pmax')
        assert isinstance(required, list)
        assert 'account_id' in required
        assert 'campaign_name' in required

    def test_get_schema_examples(self):
        """Test extracting examples from schema"""
        examples = get_schema_examples('create_pmax')
        assert isinstance(examples, dict)
        assert 'account_id' in examples


class TestCreatePMaxSchema:
    """Test create_pmax schema validation"""

    def test_valid_minimal_params(self):
        """Test validation with minimal required params"""
        params = {
            "account_id": "1234567890",
            "campaign_name": "Test Campaign",
            "daily_budget_micros": 1500000000
        }
        is_valid, error = validate_params('create_pmax', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_with_currency(self):
        """Test validation with daily_budget_currency instead of micros"""
        params = {
            "account_id": "1234567890",
            "campaign_name": "Test Campaign",
            "daily_budget_currency": 1500
        }
        is_valid, error = validate_params('create_pmax', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_full_params(self):
        """Test validation with all optional params"""
        params = {
            "account_id": "1234567890",
            "campaign_name": "Test Campaign",
            "daily_budget_micros": 1500000000,
            "target_roas": 2.5,
            "merchant_center_id": "123456789",
            "feed_label": "promo_nov2025",
            "start_date": "2025-11-10",
            "status": "PAUSED",
            "country_codes": ["TH"],
            "language_codes": ["th"]
        }
        is_valid, error = validate_params('create_pmax', params)
        assert is_valid, f"Validation failed: {error}"

    def test_invalid_account_id_format(self):
        """Test validation fails with invalid account_id"""
        params = {
            "account_id": "123",  # Too short
            "campaign_name": "Test Campaign",
            "daily_budget_micros": 1500000000
        }
        is_valid, error = validate_params('create_pmax', params)
        assert not is_valid
        assert "account_id" in error.lower() or "pattern" in error.lower()

    def test_invalid_date_format(self):
        """Test validation fails with invalid date format"""
        params = {
            "account_id": "1234567890",
            "campaign_name": "Test Campaign",
            "daily_budget_micros": 1500000000,
            "start_date": "2025/11/10"  # Wrong format
        }
        is_valid, error = validate_params('create_pmax', params)
        assert not is_valid

    def test_missing_required_field(self):
        """Test validation fails when required field is missing"""
        params = {
            "account_id": "1234567890",
            # Missing campaign_name
            "daily_budget_micros": 1500000000
        }
        is_valid, error = validate_params('create_pmax', params)
        assert not is_valid
        assert "campaign_name" in error.lower()


class TestUpdateBudgetSchema:
    """Test update_budget schema validation"""

    def test_valid_set_budget(self):
        """Test validation with SET adjustment type"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "new_daily_budget_micros": 2000000000
        }
        is_valid, error = validate_params('update_budget', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_percentage_increase(self):
        """Test validation with percentage adjustment"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "adjustment_type": "INCREASE_BY_PERCENT",
            "adjustment_value": 20
        }
        is_valid, error = validate_params('update_budget', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_with_resource_name(self):
        """Test validation with campaign_resource_name"""
        params = {
            "account_id": "1234567890",
            "campaign_resource_name": "customers/1234567890/campaigns/9876543210",
            "new_daily_budget_currency": 2000
        }
        is_valid, error = validate_params('update_budget', params)
        assert is_valid, f"Validation failed: {error}"


class TestSetTargetROASSchema:
    """Test set_target_roas schema validation"""

    def test_valid_basic(self):
        """Test validation with basic params"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "target_roas": 3.0
        }
        is_valid, error = validate_params('set_target_roas', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_with_bid_limits(self):
        """Test validation with bid ceiling and floor"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "target_roas": 2.5,
            "cpc_bid_ceiling_micros": 5000000,
            "cpc_bid_floor_micros": 1000000
        }
        is_valid, error = validate_params('set_target_roas', params)
        assert is_valid, f"Validation failed: {error}"

    def test_invalid_roas_too_low(self):
        """Test validation fails with too low ROAS"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "target_roas": 0.001  # Too low
        }
        is_valid, error = validate_params('set_target_roas', params)
        assert not is_valid


class TestPauseCampaignSchema:
    """Test pause_campaign schema validation"""

    def test_valid_single_campaign(self):
        """Test validation with single campaign_id"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210"
        }
        is_valid, error = validate_params('pause_campaign', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_multiple_campaigns(self):
        """Test validation with multiple campaign_ids"""
        params = {
            "account_id": "1234567890",
            "campaign_ids": ["9876543210", "9876543211", "9876543212"]
        }
        is_valid, error = validate_params('pause_campaign', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_pattern_with_confirm(self):
        """Test validation with pattern requires confirm"""
        params = {
            "account_id": "1234567890",
            "campaign_name_pattern": "Test*",
            "confirm": True
        }
        is_valid, error = validate_params('pause_campaign', params)
        assert is_valid, f"Validation failed: {error}"


class TestEnableCampaignSchema:
    """Test enable_campaign schema validation"""

    def test_valid_with_safety_check(self):
        """Test validation with safety_check enabled"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "safety_check": True
        }
        is_valid, error = validate_params('enable_campaign', params)
        assert is_valid, f"Validation failed: {error}"


class TestAttachMerchantCenterSchema:
    """Test attach_merchant_center schema validation"""

    def test_valid_minimal(self):
        """Test validation with minimal params"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "merchant_center_id": "123456789"
        }
        is_valid, error = validate_params('attach_merchant_center', params)
        assert is_valid, f"Validation failed: {error}"

    def test_valid_with_feed_label(self):
        """Test validation with feed_label"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "merchant_center_id": "123456789",
            "feed_label": "promo_nov2025",
            "sales_country": "TH",
            "language_code": "th"
        }
        is_valid, error = validate_params('attach_merchant_center', params)
        assert is_valid, f"Validation failed: {error}"

    def test_invalid_country_code(self):
        """Test validation fails with invalid country code"""
        params = {
            "account_id": "1234567890",
            "campaign_id": "9876543210",
            "merchant_center_id": "123456789",
            "sales_country": "Thailand"  # Should be 2-letter code
        }
        is_valid, error = validate_params('attach_merchant_center', params)
        assert not is_valid


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
