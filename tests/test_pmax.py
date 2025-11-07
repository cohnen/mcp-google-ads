"""
Unit tests for Performance Max campaign operations
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mutate.pmax import PerformanceMaxCampaign, create_pmax_campaign_full


class TestPerformanceMaxCampaign:
    """Test Performance Max campaign class"""

    def test_init(self):
        """Test initialization"""
        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        pmax = PerformanceMaxCampaign(creds, headers, "v19")

        assert pmax.credentials == creds
        assert pmax.headers == headers
        assert pmax.api_version == "v19"
        assert pmax.base_url == "https://googleads.googleapis.com/v19"

    @patch('requests.post')
    def test_create_campaign_budget(self, mock_post):
        """Test creating campaign budget"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"resourceName": "customers/1234567890/campaignBudgets/111111"}
            ]
        }
        mock_post.return_value = mock_response

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax._create_campaign_budget(
            "1234567890", 1500000000, "Test Budget"
        )

        assert result == "customers/1234567890/campaignBudgets/111111"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_campaign_minimal(self, mock_post):
        """Test creating minimal campaign"""
        # Mock budget creation
        budget_response = Mock()
        budget_response.status_code = 200
        budget_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaignBudgets/111111"}]
        }

        # Mock campaign creation
        campaign_response = Mock()
        campaign_response.status_code = 200
        campaign_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaigns/222222"}]
        }

        mock_post.side_effect = [budget_response, campaign_response]

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax.create_campaign(
            customer_id="1234567890",
            campaign_name="Test Campaign",
            budget_amount_micros=1500000000,
        )

        assert result["campaign_resource_name"] == "customers/1234567890/campaigns/222222"
        assert result["budget_resource_name"] == "customers/1234567890/campaignBudgets/111111"
        assert result["status"] == "PAUSED"
        assert mock_post.call_count == 2

    @patch('requests.post')
    def test_create_campaign_with_roas(self, mock_post):
        """Test creating campaign with target ROAS"""
        budget_response = Mock()
        budget_response.status_code = 200
        budget_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaignBudgets/111111"}]
        }

        campaign_response = Mock()
        campaign_response.status_code = 200
        campaign_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaigns/222222"}]
        }

        mock_post.side_effect = [budget_response, campaign_response]

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax.create_campaign(
            customer_id="1234567890",
            campaign_name="Test Campaign",
            budget_amount_micros=1500000000,
            target_roas=2.5,
        )

        assert result["campaign_resource_name"] == "customers/1234567890/campaigns/222222"
        # Verify that maximize_conversion_value with targetRoas was sent
        call_args = mock_post.call_args_list[1]
        payload = call_args[1]["json"]
        assert "maximizeConversionValue" in payload["operations"][0]["create"]
        assert payload["operations"][0]["create"]["maximizeConversionValue"]["targetRoas"] == 2.5

    @patch('requests.post')
    def test_create_campaign_with_dates(self, mock_post):
        """Test creating campaign with start and end dates"""
        budget_response = Mock()
        budget_response.status_code = 200
        budget_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaignBudgets/111111"}]
        }

        campaign_response = Mock()
        campaign_response.status_code = 200
        campaign_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaigns/222222"}]
        }

        mock_post.side_effect = [budget_response, campaign_response]

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax.create_campaign(
            customer_id="1234567890",
            campaign_name="Test Campaign",
            budget_amount_micros=1500000000,
            start_date="2025-11-10",
            end_date="2025-12-31",
        )

        assert result["campaign_resource_name"] == "customers/1234567890/campaigns/222222"
        # Verify dates were formatted correctly (dashes removed)
        call_args = mock_post.call_args_list[1]
        payload = call_args[1]["json"]
        assert payload["operations"][0]["create"]["startDate"] == "20251110"
        assert payload["operations"][0]["create"]["endDate"] == "20251231"

    @patch('requests.post')
    def test_create_asset_group(self, mock_post):
        """Test creating asset group"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/assetGroups/333333"}]
        }
        mock_post.return_value = mock_response

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax.create_asset_group(
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/222222",
            asset_group_name="Test Assets",
            final_urls=["https://example.com"],
        )

        assert result == "customers/1234567890/assetGroups/333333"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_attach_merchant_center(self, mock_post):
        """Test attaching Merchant Center feed"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{}]}
        mock_post.return_value = mock_response

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        result = pmax.attach_merchant_center_feed(
            customer_id="1234567890",
            campaign_resource_name="customers/1234567890/campaigns/222222",
            merchant_center_id="123456789",
            feed_label="promo",
        )

        assert result["success"] is True
        assert result["merchant_center_id"] == "123456789"
        assert result["feed_label"] == "promo"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_campaign_error_budget(self, mock_post):
        """Test error handling when budget creation fails"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Budget creation failed"
        mock_post.return_value = mock_response

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        with pytest.raises(Exception) as exc_info:
            pmax.create_campaign(
                customer_id="1234567890",
                campaign_name="Test Campaign",
                budget_amount_micros=1500000000,
            )

        assert "Failed to create budget" in str(exc_info.value)

    @patch('requests.post')
    def test_create_campaign_error_campaign(self, mock_post):
        """Test error handling when campaign creation fails"""
        # Budget succeeds
        budget_response = Mock()
        budget_response.status_code = 200
        budget_response.json.return_value = {
            "results": [{"resourceName": "customers/1234567890/campaignBudgets/111111"}]
        }

        # Campaign fails
        campaign_response = Mock()
        campaign_response.status_code = 400
        campaign_response.text = "Campaign creation failed"

        mock_post.side_effect = [budget_response, campaign_response]

        creds = Mock()
        headers = {"Authorization": "Bearer token"}
        pmax = PerformanceMaxCampaign(creds, headers)

        with pytest.raises(Exception) as exc_info:
            pmax.create_campaign(
                customer_id="1234567890",
                campaign_name="Test Campaign",
                budget_amount_micros=1500000000,
            )

        assert "Failed to create campaign" in str(exc_info.value)


class TestCreatePMaxCampaignFull:
    """Test full campaign creation function"""

    @patch('mutate.pmax.PerformanceMaxCampaign')
    def test_create_with_currency(self, mock_pmax_class):
        """Test creating campaign with currency (not micros)"""
        mock_pmax = Mock()
        mock_pmax.create_campaign.return_value = {
            "campaign_resource_name": "customers/1234567890/campaigns/222222",
            "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
            "status": "PAUSED",
        }
        mock_pmax_class.return_value = mock_pmax

        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        result = create_pmax_campaign_full(
            credentials=creds,
            headers=headers,
            account_id="1234567890",
            campaign_name="Test Campaign",
            daily_budget_currency=1500,  # 1500 THB
        )

        assert result["success"] is True
        assert result["campaign_name"] == "Test Campaign"
        # Verify that currency was converted to micros (1500 * 1000000)
        mock_pmax.create_campaign.assert_called_once()
        call_args = mock_pmax.create_campaign.call_args
        assert call_args[1]["budget_amount_micros"] == 1500000000

    @patch('mutate.pmax.PerformanceMaxCampaign')
    def test_create_with_micros(self, mock_pmax_class):
        """Test creating campaign with micros directly"""
        mock_pmax = Mock()
        mock_pmax.create_campaign.return_value = {
            "campaign_resource_name": "customers/1234567890/campaigns/222222",
            "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
            "status": "PAUSED",
        }
        mock_pmax_class.return_value = mock_pmax

        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        result = create_pmax_campaign_full(
            credentials=creds,
            headers=headers,
            account_id="1234567890",
            campaign_name="Test Campaign",
            daily_budget_micros=1500000000,
        )

        assert result["success"] is True
        mock_pmax.create_campaign.assert_called_once()

    @patch('mutate.pmax.PerformanceMaxCampaign')
    def test_create_with_asset_group(self, mock_pmax_class):
        """Test creating campaign with asset group"""
        mock_pmax = Mock()
        mock_pmax.create_campaign.return_value = {
            "campaign_resource_name": "customers/1234567890/campaigns/222222",
            "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
            "status": "PAUSED",
        }
        mock_pmax.create_asset_group.return_value = "customers/1234567890/assetGroups/333333"
        mock_pmax_class.return_value = mock_pmax

        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        result = create_pmax_campaign_full(
            credentials=creds,
            headers=headers,
            account_id="1234567890",
            campaign_name="Test Campaign",
            daily_budget_currency=1500,
            final_url="https://example.com",
        )

        assert result["success"] is True
        assert "asset_group_resource_name" in result
        mock_pmax.create_asset_group.assert_called_once()

    @patch('mutate.pmax.PerformanceMaxCampaign')
    def test_create_with_merchant_center(self, mock_pmax_class):
        """Test creating campaign with Merchant Center"""
        mock_pmax = Mock()
        mock_pmax.create_campaign.return_value = {
            "campaign_resource_name": "customers/1234567890/campaigns/222222",
            "budget_resource_name": "customers/1234567890/campaignBudgets/111111",
            "status": "PAUSED",
        }
        mock_pmax.attach_merchant_center_feed.return_value = {
            "success": True,
            "merchant_center_id": "123456789",
            "feed_label": "promo",
        }
        mock_pmax_class.return_value = mock_pmax

        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        result = create_pmax_campaign_full(
            credentials=creds,
            headers=headers,
            account_id="1234567890",
            campaign_name="Test Campaign",
            daily_budget_currency=1500,
            merchant_center_id="123456789",
            feed_label="promo",
        )

        assert result["success"] is True
        assert result["merchant_center_attached"] is True
        assert result["merchant_center_id"] == "123456789"
        mock_pmax.attach_merchant_center_feed.assert_called_once()

    def test_create_without_budget(self):
        """Test that error is raised when no budget is provided"""
        creds = Mock()
        headers = {"Authorization": "Bearer token"}

        with pytest.raises(ValueError) as exc_info:
            create_pmax_campaign_full(
                credentials=creds,
                headers=headers,
                account_id="1234567890",
                campaign_name="Test Campaign",
                # No budget provided
            )

        assert "daily_budget_micros or daily_budget_currency must be provided" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
