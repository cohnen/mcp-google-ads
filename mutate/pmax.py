"""
Performance Max Campaign Operations
Functions for creating and managing Performance Max campaigns
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PerformanceMaxCampaign:
    """Handler for Performance Max campaign operations"""

    def __init__(self, credentials, headers, api_version="v19"):
        """
        Initialize Performance Max campaign handler

        Args:
            credentials: Google Auth credentials
            headers: API request headers
            api_version: Google Ads API version (default: v19)
        """
        self.credentials = credentials
        self.headers = headers
        self.api_version = api_version
        self.base_url = f"https://googleads.googleapis.com/{api_version}"

    def create_campaign(
        self,
        customer_id: str,
        campaign_name: str,
        budget_amount_micros: int,
        target_roas: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: str = "PAUSED",
    ) -> Dict[str, Any]:
        """
        Create a Performance Max campaign with budget

        Args:
            customer_id: Formatted customer ID (10 digits)
            campaign_name: Name of the campaign
            budget_amount_micros: Daily budget in micros
            target_roas: Optional target ROAS (e.g., 2.5 for 250%)
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            status: Campaign status (PAUSED or ENABLED)

        Returns:
            Dictionary with campaign and budget resource names

        Raises:
            Exception: If API call fails
        """
        import requests

        logger.info(f"Creating Performance Max campaign: {campaign_name}")

        # Step 1: Create Campaign Budget
        budget_resource_name = self._create_campaign_budget(
            customer_id, budget_amount_micros, f"{campaign_name} Budget"
        )
        logger.info(f"Created budget: {budget_resource_name}")

        # Step 2: Create Campaign
        campaign_operations = {
            "operations": [
                {
                    "create": {
                        "name": campaign_name,
                        "status": status,
                        "advertisingChannelType": "PERFORMANCE_MAX",
                        "campaignBudget": budget_resource_name,
                    }
                }
            ]
        }

        # Add bidding strategy
        if target_roas:
            campaign_operations["operations"][0]["create"]["maximizeConversionValue"] = {
                "targetRoas": target_roas
            }
        else:
            campaign_operations["operations"][0]["create"]["maximizeConversionValue"] = {}

        # Add start date
        if start_date:
            campaign_operations["operations"][0]["create"]["startDate"] = start_date.replace("-", "")

        # Add end date
        if end_date:
            campaign_operations["operations"][0]["create"]["endDate"] = end_date.replace("-", "")

        # Make API call to create campaign
        url = f"{self.base_url}/customers/{customer_id}/campaigns:mutate"

        logger.debug(f"Campaign creation request: {json.dumps(campaign_operations, indent=2)}")

        response = requests.post(url, headers=self.headers, json=campaign_operations)

        if response.status_code != 200:
            error_msg = f"Failed to create campaign: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        result = response.json()
        campaign_resource_name = result["results"][0]["resourceName"]

        logger.info(f"Created campaign: {campaign_resource_name}")

        return {
            "campaign_resource_name": campaign_resource_name,
            "budget_resource_name": budget_resource_name,
            "status": status,
        }

    def _create_campaign_budget(
        self, customer_id: str, amount_micros: int, budget_name: str
    ) -> str:
        """
        Create a campaign budget

        Args:
            customer_id: Formatted customer ID
            amount_micros: Budget amount in micros
            budget_name: Name of the budget

        Returns:
            Budget resource name

        Raises:
            Exception: If API call fails
        """
        import requests

        budget_operations = {
            "operations": [
                {
                    "create": {
                        "name": budget_name,
                        "amountMicros": str(amount_micros),
                        "deliveryMethod": "STANDARD",
                        "explicitlyShared": False,
                    }
                }
            ]
        }

        url = f"{self.base_url}/customers/{customer_id}/campaignBudgets:mutate"

        logger.debug(f"Budget creation request: {json.dumps(budget_operations, indent=2)}")

        response = requests.post(url, headers=self.headers, json=budget_operations)

        if response.status_code != 200:
            error_msg = f"Failed to create budget: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        result = response.json()
        return result["results"][0]["resourceName"]

    def create_asset_group(
        self,
        customer_id: str,
        campaign_resource_name: str,
        asset_group_name: str,
        final_urls: List[str],
    ) -> str:
        """
        Create an asset group for Performance Max campaign

        Args:
            customer_id: Formatted customer ID
            campaign_resource_name: Campaign resource name
            asset_group_name: Name of the asset group
            final_urls: List of final URLs

        Returns:
            Asset group resource name

        Raises:
            Exception: If API call fails
        """
        import requests

        asset_group_operations = {
            "operations": [
                {
                    "create": {
                        "name": asset_group_name,
                        "campaign": campaign_resource_name,
                        "finalUrls": final_urls,
                        "status": "ENABLED",
                    }
                }
            ]
        }

        url = f"{self.base_url}/customers/{customer_id}/assetGroups:mutate"

        logger.debug(f"Asset group creation request: {json.dumps(asset_group_operations, indent=2)}")

        response = requests.post(url, headers=self.headers, json=asset_group_operations)

        if response.status_code != 200:
            error_msg = f"Failed to create asset group: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        result = response.json()
        asset_group_resource_name = result["results"][0]["resourceName"]

        logger.info(f"Created asset group: {asset_group_resource_name}")

        return asset_group_resource_name

    def attach_merchant_center_feed(
        self,
        customer_id: str,
        campaign_resource_name: str,
        merchant_center_id: str,
        feed_label: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Attach Merchant Center feed to Performance Max campaign

        Args:
            customer_id: Formatted customer ID
            campaign_resource_name: Campaign resource name
            merchant_center_id: Merchant Center account ID
            feed_label: Optional feed label for filtering

        Returns:
            Result dictionary

        Raises:
            Exception: If API call fails
        """
        import requests

        # Create shopping setting for the campaign
        shopping_setting = {
            "merchantId": merchant_center_id,
            "enableLocal": True,
        }

        if feed_label:
            shopping_setting["feedLabel"] = feed_label

        # Update campaign with shopping setting
        update_operations = {
            "operations": [
                {
                    "update": {
                        "resourceName": campaign_resource_name,
                        "shoppingSetting": shopping_setting,
                    },
                    "updateMask": "shoppingSetting",
                }
            ]
        }

        url = f"{self.base_url}/customers/{customer_id}/campaigns:mutate"

        logger.debug(f"Merchant Center attachment request: {json.dumps(update_operations, indent=2)}")

        response = requests.post(url, headers=self.headers, json=update_operations)

        if response.status_code != 200:
            error_msg = f"Failed to attach Merchant Center: {response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

        result = response.json()

        logger.info(f"Attached Merchant Center {merchant_center_id} to campaign")

        return {
            "success": True,
            "merchant_center_id": merchant_center_id,
            "feed_label": feed_label,
        }


def create_pmax_campaign_full(
    credentials,
    headers,
    account_id: str,
    campaign_name: str,
    daily_budget_micros: Optional[int] = None,
    daily_budget_currency: Optional[float] = None,
    target_roas: Optional[float] = None,
    merchant_center_id: Optional[str] = None,
    feed_label: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: str = "PAUSED",
    final_url: Optional[str] = None,
    country_codes: Optional[List[str]] = None,
    language_codes: Optional[List[str]] = None,
    asset_group_name: Optional[str] = None,
    api_version: str = "v19",
) -> Dict[str, Any]:
    """
    Create a complete Performance Max campaign with all settings

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        account_id: Google Ads customer ID
        campaign_name: Campaign name
        daily_budget_micros: Daily budget in micros
        daily_budget_currency: Daily budget in currency (will be converted)
        target_roas: Target ROAS (optional)
        merchant_center_id: Merchant Center ID (optional)
        feed_label: Feed label for filtering (optional)
        start_date: Start date YYYY-MM-DD (optional)
        end_date: End date YYYY-MM-DD (optional)
        status: Campaign status (PAUSED or ENABLED)
        final_url: Final URL for asset group
        country_codes: Target country codes (optional)
        language_codes: Target language codes (optional)
        asset_group_name: Asset group name (optional)
        api_version: API version

    Returns:
        Dictionary with all created resource names and details

    Raises:
        ValueError: If required parameters are missing or invalid
        Exception: If API calls fail
    """
    from mutate.utils import format_customer_id, currency_to_micros

    # Validate and format customer ID
    formatted_customer_id = format_customer_id(account_id)

    # Convert budget if needed
    if daily_budget_currency:
        budget_micros = currency_to_micros(daily_budget_currency)
    elif daily_budget_micros:
        budget_micros = daily_budget_micros
    else:
        raise ValueError("Either daily_budget_micros or daily_budget_currency must be provided")

    # Initialize PMax handler
    pmax = PerformanceMaxCampaign(credentials, headers, api_version)

    # Step 1: Create campaign with budget
    campaign_result = pmax.create_campaign(
        customer_id=formatted_customer_id,
        campaign_name=campaign_name,
        budget_amount_micros=budget_micros,
        target_roas=target_roas,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )

    result = {
        "success": True,
        "campaign_resource_name": campaign_result["campaign_resource_name"],
        "budget_resource_name": campaign_result["budget_resource_name"],
        "campaign_name": campaign_name,
        "status": status,
    }

    # Step 2: Create asset group if final_url provided
    if final_url:
        ag_name = asset_group_name or f"{campaign_name} Assets"
        asset_group_resource_name = pmax.create_asset_group(
            customer_id=formatted_customer_id,
            campaign_resource_name=campaign_result["campaign_resource_name"],
            asset_group_name=ag_name,
            final_urls=[final_url],
        )
        result["asset_group_resource_name"] = asset_group_resource_name
        result["asset_group_name"] = ag_name

    # Step 3: Attach Merchant Center if provided
    if merchant_center_id:
        merchant_result = pmax.attach_merchant_center_feed(
            customer_id=formatted_customer_id,
            campaign_resource_name=campaign_result["campaign_resource_name"],
            merchant_center_id=merchant_center_id,
            feed_label=feed_label,
        )
        result["merchant_center_attached"] = True
        result["merchant_center_id"] = merchant_center_id
        if feed_label:
            result["feed_label"] = feed_label

    # Add additional info
    if target_roas:
        result["target_roas"] = target_roas
    if start_date:
        result["start_date"] = start_date
    if end_date:
        result["end_date"] = end_date

    logger.info(f"Successfully created Performance Max campaign: {campaign_name}")

    return result
