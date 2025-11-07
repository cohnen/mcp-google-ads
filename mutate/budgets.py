"""
Campaign Budget Management Operations
Functions for updating campaign budgets
"""

import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def get_campaign_budget(
    headers: Dict[str, str],
    customer_id: str,
    campaign_resource_name: str,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Get current budget for a campaign

    Args:
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_resource_name: Full campaign resource name
        api_version: API version

    Returns:
        Dictionary with budget info

    Raises:
        Exception: If API call fails
    """
    base_url = f"https://googleads.googleapis.com/{api_version}"

    # Query to get campaign budget
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.campaign_budget,
            campaign_budget.amount_micros
        FROM campaign
        WHERE campaign.resource_name = '{campaign_resource_name}'
    """

    url = f"{base_url}/customers/{customer_id}/googleAds:search"
    payload = {"query": query}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        error_msg = f"Failed to get campaign budget: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    results = response.json()
    if not results.get('results'):
        raise Exception(f"Campaign not found: {campaign_resource_name}")

    result = results['results'][0]
    campaign_budget = result.get('campaignBudget', {})

    return {
        "campaign_id": result.get('campaign', {}).get('id'),
        "campaign_name": result.get('campaign', {}).get('name'),
        "budget_resource_name": result.get('campaign', {}).get('campaignBudget'),
        "current_amount_micros": int(campaign_budget.get('amountMicros', 0))
    }


def update_campaign_budget(
    credentials,
    headers: Dict[str, str],
    customer_id: str,
    campaign_id: Optional[str] = None,
    campaign_resource_name: Optional[str] = None,
    new_amount_micros: Optional[int] = None,
    adjustment_type: str = "SET",
    adjustment_value: Optional[float] = None,
    api_version: str = "v19"
) -> Dict[str, Any]:
    """
    Update campaign budget

    Args:
        credentials: Google Auth credentials
        headers: API request headers
        customer_id: Formatted customer ID
        campaign_id: Campaign ID (if not using resource_name)
        campaign_resource_name: Full campaign resource name
        new_amount_micros: New budget amount in micros
        adjustment_type: SET, INCREASE_BY_PERCENT, DECREASE_BY_PERCENT, etc.
        adjustment_value: Value for adjustment
        api_version: API version

    Returns:
        Dictionary with update results

    Raises:
        ValueError: If parameters are invalid
        Exception: If API call fails
    """
    from mutate.utils import format_customer_id, build_campaign_resource_name

    formatted_customer_id = format_customer_id(customer_id)
    base_url = f"https://googleads.googleapis.com/{api_version}"

    # Build campaign resource name if needed
    if not campaign_resource_name:
        if not campaign_id:
            raise ValueError("Either campaign_id or campaign_resource_name must be provided")
        campaign_resource_name = build_campaign_resource_name(formatted_customer_id, campaign_id)

    # Get current budget info
    logger.info(f"Getting current budget for campaign: {campaign_resource_name}")
    budget_info = get_campaign_budget(headers, formatted_customer_id, campaign_resource_name, api_version)

    current_amount = budget_info['current_amount_micros']
    budget_resource_name = budget_info['budget_resource_name']

    # Calculate new budget amount based on adjustment type
    if adjustment_type == "SET":
        if not new_amount_micros:
            raise ValueError("new_amount_micros is required for SET adjustment type")
        final_amount = new_amount_micros

    elif adjustment_type == "INCREASE_BY_PERCENT":
        if adjustment_value is None:
            raise ValueError("adjustment_value is required for INCREASE_BY_PERCENT")
        increase = int(current_amount * (adjustment_value / 100))
        final_amount = current_amount + increase
        logger.info(f"Increasing budget by {adjustment_value}%: {current_amount} + {increase} = {final_amount}")

    elif adjustment_type == "DECREASE_BY_PERCENT":
        if adjustment_value is None:
            raise ValueError("adjustment_value is required for DECREASE_BY_PERCENT")
        decrease = int(current_amount * (adjustment_value / 100))
        final_amount = current_amount - decrease
        logger.info(f"Decreasing budget by {adjustment_value}%: {current_amount} - {decrease} = {final_amount}")

    elif adjustment_type == "INCREASE_BY_AMOUNT":
        if adjustment_value is None:
            raise ValueError("adjustment_value is required for INCREASE_BY_AMOUNT")
        final_amount = current_amount + int(adjustment_value)
        logger.info(f"Increasing budget by {adjustment_value}: {current_amount} + {adjustment_value} = {final_amount}")

    elif adjustment_type == "DECREASE_BY_AMOUNT":
        if adjustment_value is None:
            raise ValueError("adjustment_value is required for DECREASE_BY_AMOUNT")
        final_amount = current_amount - int(adjustment_value)
        logger.info(f"Decreasing budget by {adjustment_value}: {current_amount} - {adjustment_value} = {final_amount}")

    else:
        raise ValueError(f"Invalid adjustment_type: {adjustment_type}")

    # Ensure budget is not negative
    if final_amount < 0:
        raise ValueError(f"Resulting budget would be negative: {final_amount}")

    # Ensure minimum budget (1 million micros = 1 currency unit)
    if final_amount < 1000000:
        raise ValueError(f"Budget too low: {final_amount} micros (minimum: 1000000)")

    # Update the budget
    logger.info(f"Updating budget {budget_resource_name} from {current_amount} to {final_amount}")

    update_operations = {
        "operations": [
            {
                "update": {
                    "resourceName": budget_resource_name,
                    "amountMicros": str(final_amount)
                },
                "updateMask": "amountMicros"
            }
        ]
    }

    url = f"{base_url}/customers/{formatted_customer_id}/campaignBudgets:mutate"

    response = requests.post(url, headers=headers, json=update_operations)

    if response.status_code != 200:
        error_msg = f"Failed to update budget: {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    result = response.json()

    logger.info(f"Successfully updated budget: {budget_resource_name}")

    from mutate.utils import micros_to_currency

    return {
        "success": True,
        "budget_resource_name": budget_resource_name,
        "campaign_resource_name": campaign_resource_name,
        "campaign_name": budget_info['campaign_name'],
        "previous_amount_micros": current_amount,
        "new_amount_micros": final_amount,
        "previous_amount_currency": micros_to_currency(current_amount),
        "new_amount_currency": micros_to_currency(final_amount),
        "adjustment_type": adjustment_type,
        "change_micros": final_amount - current_amount,
        "change_currency": micros_to_currency(final_amount - current_amount),
        "change_percent": ((final_amount - current_amount) / current_amount * 100) if current_amount > 0 else 0
    }
