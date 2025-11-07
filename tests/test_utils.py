"""
Unit tests for mutate utility functions
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mutate.utils import (
    format_customer_id,
    micros_to_currency,
    currency_to_micros,
    validate_date_format,
    build_campaign_resource_name,
    parse_resource_name,
    sanitize_campaign_name,
)


class TestFormatCustomerId:
    """Test customer ID formatting"""

    def test_format_string_with_dashes(self):
        """Test formatting customer ID with dashes"""
        assert format_customer_id("123-456-7890") == "1234567890"

    def test_format_integer(self):
        """Test formatting integer customer ID"""
        assert format_customer_id(1234567890) == "1234567890"

    def test_format_short_id(self):
        """Test formatting short customer ID (adds leading zeros)"""
        assert format_customer_id("12345") == "0000012345"

    def test_format_with_quotes(self):
        """Test formatting customer ID with quotes"""
        assert format_customer_id('"1234567890"') == "1234567890"

    def test_format_with_special_chars(self):
        """Test formatting customer ID with special characters"""
        assert format_customer_id("123-456-7890!@#") == "1234567890"


class TestCurrencyConversion:
    """Test currency conversion functions"""

    def test_micros_to_currency(self):
        """Test converting micros to currency"""
        assert micros_to_currency(1500000000) == 1500.0
        assert micros_to_currency(1000000) == 1.0
        assert micros_to_currency(0) == 0.0

    def test_currency_to_micros(self):
        """Test converting currency to micros"""
        assert currency_to_micros(1500) == 1500000000
        assert currency_to_micros(1.5) == 1500000
        assert currency_to_micros(0) == 0

    def test_round_trip_conversion(self):
        """Test round-trip conversion"""
        original = 1234.56
        micros = currency_to_micros(original)
        back_to_currency = micros_to_currency(micros)
        assert abs(original - back_to_currency) < 0.01


class TestDateValidation:
    """Test date format validation"""

    def test_valid_date(self):
        """Test valid date formats"""
        assert validate_date_format("2025-11-10") is True
        assert validate_date_format("2025-01-01") is True
        assert validate_date_format("2025-12-31") is True

    def test_invalid_date_format(self):
        """Test invalid date formats"""
        assert validate_date_format("2025/11/10") is False
        assert validate_date_format("11-10-2025") is False
        assert validate_date_format("2025-13-01") is False
        assert validate_date_format("not-a-date") is False


class TestResourceNames:
    """Test resource name building and parsing"""

    def test_build_campaign_resource_name(self):
        """Test building campaign resource name"""
        resource_name = build_campaign_resource_name("1234567890", "9876543210")
        assert resource_name == "customers/1234567890/campaigns/9876543210"

    def test_build_with_formatted_customer_id(self):
        """Test building with customer ID that needs formatting"""
        resource_name = build_campaign_resource_name("123-456-7890", "9876543210")
        assert resource_name == "customers/1234567890/campaigns/9876543210"

    def test_parse_resource_name(self):
        """Test parsing resource name"""
        resource_name = "customers/1234567890/campaigns/9876543210"
        parsed = parse_resource_name(resource_name)

        assert parsed['customer_id'] == "1234567890"
        assert parsed['resource_type'] == "campaigns"
        assert parsed['resource_id'] == "9876543210"

    def test_parse_invalid_resource_name(self):
        """Test parsing invalid resource name"""
        with pytest.raises(ValueError):
            parse_resource_name("invalid/format")


class TestCampaignNameSanitization:
    """Test campaign name sanitization"""

    def test_sanitize_normal_name(self):
        """Test sanitizing normal campaign name"""
        name = "Test Campaign 2025"
        assert sanitize_campaign_name(name) == "Test Campaign 2025"

    def test_sanitize_with_whitespace(self):
        """Test sanitizing name with leading/trailing whitespace"""
        name = "  Test Campaign  "
        assert sanitize_campaign_name(name) == "Test Campaign"

    def test_sanitize_too_long(self):
        """Test sanitizing name that's too long"""
        name = "A" * 300
        sanitized = sanitize_campaign_name(name)
        assert len(sanitized) == 255

    def test_sanitize_empty_raises_error(self):
        """Test that empty name raises error"""
        with pytest.raises(ValueError):
            sanitize_campaign_name("")

    def test_sanitize_whitespace_only_raises_error(self):
        """Test that whitespace-only name raises error"""
        with pytest.raises(ValueError):
            sanitize_campaign_name("   ")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
