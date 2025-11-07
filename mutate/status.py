"""
Campaign Status Management Operations
Functions for pausing and enabling campaigns
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def set_campaign_status(
    credentials,
    headers: Dict[str, str],
    customer_id: str,
    campaign_ids: List[str],
    status: str,  # "PAUSED" or "ENABLED"
    safety_check: bool = True,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Set status for one or more campaigns

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_ids: List of campaign IDs
        status: Target status ("PAUSED" or "ENABLED")
        safety_check: Perform safety checks before enabling
        api_version: API version

    Returns:
        Dictionary with results for each campaign

    Raises:
        ValueError: If parameters are invalid
        Exception: If API call fails
    """
    from mutate.utils import format_customer_id, build_campaign_resource_name

    if status not in ["PAUSED", "ENABLED"]:
        raise ValueError(f"Invalid status: {status}. Must be PAUSED or ENABLED")

    formatted_customer_id = format_customer_id(customer_id)
    base_url = f"https://googleads.googleapis.com/{api_version}"

    results = []
    failed = []

    for campaign_id in campaign_ids:
        try:
            campaign_resource_name = build_campaign_resource_name(formatted_customer_id, campaign_id)

            # Safety check if enabling
            if status == "ENABLED" and safety_check:
                logger.info(f"Performing safety check for campaign: {campaign_resource_name}")
                check_result = _safety_check_campaign(headers, formatted_customer_id, campaign_resource_name, api_version)

                if not check_result["safe"]:
                    failed.append({
                        "campaign_id": campaign_id,
                        "campaign_resource_name": campaign_resource_name,
                        "error": "Safety check failed",
                        "issues": check_result["issues"]
                    })
                    continue

            # Update campaign status
            logger.info(f"Setting campaign {campaign_resource_name} to {status}")

            update_operations = {
                "operations": [
                    {
                        "update": {
                            "resourceName": campaign_resource_name,
                            "status": status
                        },
                        "updateMask": "status"
                    }
                ]
            }

            url = f"{base_url}/customers/{formatted_customer_id}/campaigns:mutate"

            response = requests.post(url, headers=headers, json=update_operations)

            if response.status_code != 200:
                error_msg = f"Failed to update status: {response.text}"
                logger.error(error_msg)
                failed.append({
                    "campaign_id": campaign_id,
                    "campaign_resource_name": campaign_resource_name,
                    "error": error_msg
                })
                continue

            results.append({
                "campaign_id": campaign_id,
                "campaign_resource_name": campaign_resource_name,
                "previous_status": "UNKNOWN",  # We don't query this for performance
                "new_status": status,
                "success": True
            })

            logger.info(f"Successfully set campaign {campaign_resource_name} to {status}")

        except Exception as e:
            logger.error(f"Error updating campaign {campaign_id}: {str(e)}")
            failed.append({
                "campaign_id": campaign_id,
                "error": str(e)
            })

    return {
        "success": len(failed) == 0,
        "updated_count": len(results),
        "failed_count": len(failed),
        "results": results,
        "failed": failed if failed else None
    }


def _safety_check_campaign(
    headers: Dict[str, str],
    customer_id: str,
    campaign_resource_name: str,
    api_version: str
) -> Dict[str, Any]:
    """
    Perform safety checks before enabling a campaign

    Args:
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_resource_name: Campaign resource name
        api_version: API version

    Returns:
        Dictionary with safety check results
    """
    base_url = f"https://googleads.googleapis.com/{api_version}"

    issues = []

    # Query campaign details
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.campaign_budget,
            campaign_budget.amount_micros,
            campaign.advertising_channel_type
        FROM campaign
        WHERE campaign.resource_name = '{campaign_resource_name}'
    """

    url = f"{base_url}/customers/{customer_id}/googleAds:search"
    payload = {"query": query}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            issues.append(f"Could not query campaign: {response.text}")
            return {"safe": False, "issues": issues}

        results = response.json()
        if not results.get('results'):
            issues.append("Campaign not found")
            return {"safe": False, "issues": issues}

        result = results['results'][0]
        campaign_budget = result.get('campaignBudget', {})
        budget_amount = int(campaign_budget.get('amountMicros', 0))

        # Check if budget exists and is > 0
        if budget_amount <= 0:
            issues.append("Campaign has no budget or budget is 0")

        # Check if budget is too low (< 1 currency unit)
        if budget_amount < 1000000:
            issues.append(f"Campaign budget is very low: {budget_amount} micros")

        # More checks can be added here:
        # - Check if campaign has ad groups
        # - Check if ad groups have ads
        # - Check targeting settings
        # etc.

    except Exception as e:
        issues.append(f"Safety check error: {str(e)}")
        return {"safe": False, "issues": issues}

    return {
        "safe": len(issues) == 0,
        "issues": issues if issues else None
    }


def pause_campaigns(
    credentials,
    headers: Dict[str, str],
    customer_id: str,
    campaign_ids: List[str],
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Pause one or more campaigns

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_ids: List of campaign IDs to pause
        api_version: API version

    Returns:
        Dictionary with pause results
    """
    logger.info(f"Pausing {len(campaign_ids)} campaign(s)")
    return set_campaign_status(
        credentials=credentials,
        headers=headers,
        customer_id=customer_id,
        campaign_ids=campaign_ids,
        status="PAUSED",
        safety_check=False,  # No safety check needed for pausing
        api_version=api_version
    )


def enable_campaigns(
    credentials,
    headers: Dict[str, str],
    customer_id: str,
    campaign_ids: List[str],
    safety_check: bool = True,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Enable one or more campaigns

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_ids: List of campaign IDs to enable
        safety_check: Perform safety checks before enabling
        api_version: API version

    Returns:
        Dictionary with enable results
    """
    logger.info(f"Enabling {len(campaign_ids)} campaign(s) (safety_check={safety_check})")
    return set_campaign_status(
        credentials=credentials,
        headers=headers,
        customer_id=customer_id,
        campaign_ids=campaign_ids,
        status="ENABLED",
        safety_check=safety_check,
        api_version=api_version
    )


def find_campaigns_by_pattern(
    headers: Dict[str, str],
    customer_id: str,
    name_pattern: str,
    api_version: str = "v19"
) -> List[str]:
    """
    Find campaign IDs matching a name pattern

    Args:
        headers: API request headers
        customer_id: Formatted customer ID
        name_pattern: Pattern to match (e.g., "Test*")
        api_version: API version

    Returns:
        List of campaign IDs matching the pattern
    """
    base_url = f"https://googleads.googleapis.com/{api_version}"

    # Convert simple pattern to SQL LIKE pattern
    sql_pattern = name_pattern.replace('*', '%')

    query = f"""
        SELECT
            campaign.id,
            campaign.name
        FROM campaign
        WHERE campaign.name LIKE '{sql_pattern}'
    """

    url = f"{base_url}/customers/{customer_id}/googleAds:search"
    payload = {"query": query}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        error_msg = f"Failed to search campaigns: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    results = response.json()

    campaign_ids = []
    for result in results.get('results', []):
        campaign = result.get('campaign', {})
        campaign_id = campaign.get('id')
        if campaign_id:
            campaign_ids.append(str(campaign_id))

    logger.info(f"Found {len(campaign_ids)} campaigns matching pattern '{name_pattern}'")

    return campaign_ids
