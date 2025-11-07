"""
Campaign Bidding Strategy Operations
Functions for managing bidding strategies including target ROAS
"""

import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_campaign_bidding(
    headers: Dict[str, str],
    customer_id: str,
    campaign_resource_name: str,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Get current bidding strategy for a campaign

    Args:
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_resource_name: Full campaign resource name
        api_version: API version

    Returns:
        Dictionary with bidding info

    Raises:
        Exception: If API call fails
    """
    base_url = f"https://googleads.googleapis.com/{api_version}"

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.maximize_conversion_value.target_roas,
            campaign.maximize_conversion_value.cpc_bid_ceiling_micros,
            campaign.maximize_conversion_value.cpc_bid_floor_micros
        FROM campaign
        WHERE campaign.resource_name = '{campaign_resource_name}'
    """

    url = f"{base_url}/customers/{customer_id}/googleAds:search"
    payload = {"query": query}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        error_msg = f"Failed to get campaign bidding: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    results = response.json()
    if not results.get('results'):
        raise Exception(f"Campaign not found: {campaign_resource_name}")

    result = results['results'][0]
    campaign = result.get('campaign', {})
    bidding = campaign.get('maximizeConversionValue', {})

    return {
        "campaign_id": campaign.get('id'),
        "campaign_name": campaign.get('name'),
        "current_target_roas": bidding.get('targetRoas'),
        "cpc_bid_ceiling_micros": bidding.get('cpcBidCeilingMicros'),
        "cpc_bid_floor_micros": bidding.get('cpcBidFloorMicros')
    }


def set_target_roas(
    credentials,
    headers: Dict[str, str],
    customer_id: str,
    campaign_id: Optional[str] = None,
    campaign_resource_name: Optional[str] = None,
    target_roas: float = None,
    cpc_bid_ceiling_micros: Optional[int] = None,
    cpc_bid_floor_micros: Optional[int] = None,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Set or update target ROAS for a campaign

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_id: Campaign ID (if not using resource_name)
        campaign_resource_name: Full campaign resource name
        target_roas: Target ROAS value (e.g., 2.5 for 250% ROAS)
        cpc_bid_ceiling_micros: Optional max CPC bid limit
        cpc_bid_floor_micros: Optional min CPC bid limit
        api_version: API version

    Returns:
        Dictionary with update results

    Raises:
        ValueError: If parameters are invalid
        Exception: If API call fails
    """
    from mutate.utils import format_customer_id, build_campaign_resource_name

    if target_roas is None:
        raise ValueError("target_roas is required")

    if target_roas < 0.01 or target_roas > 100:
        raise ValueError(f"target_roas must be between 0.01 and 100, got: {target_roas}")

    formatted_customer_id = format_customer_id(customer_id)
    base_url = f"https://googleads.googleapis.com/{api_version}"

    # Build campaign resource name if needed
    if not campaign_resource_name:
        if not campaign_id:
            raise ValueError("Either campaign_id or campaign_resource_name must be provided")
        campaign_resource_name = build_campaign_resource_name(formatted_customer_id, campaign_id)

    # Get current bidding info
    logger.info(f"Getting current bidding for campaign: {campaign_resource_name}")
    bidding_info = get_campaign_bidding(headers, formatted_customer_id, campaign_resource_name, api_version)

    current_roas = bidding_info.get('current_target_roas')

    # Build the bidding strategy update
    maximize_conversion_value = {
        "targetRoas": target_roas
    }

    if cpc_bid_ceiling_micros is not None:
        maximize_conversion_value["cpcBidCeilingMicros"] = str(cpc_bid_ceiling_micros)

    if cpc_bid_floor_micros is not None:
        maximize_conversion_value["cpcBidFloorMicros"] = str(cpc_bid_floor_micros)

    # Update the campaign bidding strategy
    logger.info(f"Updating target ROAS for campaign {campaign_resource_name}: {current_roas} -> {target_roas}")

    update_operations = {
        "operations": [
            {
                "update": {
                    "resourceName": campaign_resource_name,
                    "maximizeConversionValue": maximize_conversion_value
                },
                "updateMask": "maximizeConversionValue"
            }
        ]
    }

    url = f"{base_url}/customers/{formatted_customer_id}/campaigns:mutate"

    response = requests.post(url, headers=headers, json=update_operations)

    if response.status_code != 200:
        error_msg = f"Failed to update target ROAS: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    result = response.json()

    logger.info(f"Successfully updated target ROAS for campaign: {campaign_resource_name}")

    response_data = {
        "success": True,
        "campaign_resource_name": campaign_resource_name,
        "campaign_name": bidding_info['campaign_name'],
        "previous_target_roas": current_roas,
        "new_target_roas": target_roas,
        "target_roas_change": target_roas - current_roas if current_roas else None
    }

    if cpc_bid_ceiling_micros is not None:
        response_data["cpc_bid_ceiling_micros"] = cpc_bid_ceiling_micros

    if cpc_bid_floor_micros is not None:
        response_data["cpc_bid_floor_micros"] = cpc_bid_floor_micros

    return response_data
