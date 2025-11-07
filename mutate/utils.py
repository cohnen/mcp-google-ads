"""
Utility functions for mutate operations
"""

from datetime import datetime
from typing import Union


def format_customer_id(customer_id: Union[str, int]) -> str:
    """
    Format customer ID to ensure it's 10 digits without dashes.

    Args:
        customer_id: Customer ID as string or int

    Returns:
        Formatted customer ID (10 digits)
    """
    customer_id = str(customer_id)
    customer_id = customer_id.replace('\"', '').replace('"', '')
    customer_id = ''.join(char for char in customer_id if char.isdigit())
    return customer_id.zfill(10)


def micros_to_currency(micros: int) -> float:
    """
    Convert micros to currency units.

    Args:
        micros: Amount in micros (1,000,000 micros = 1 currency unit)

    Returns:
        Amount in currency units

    Example:
        >>> micros_to_currency(1500000000)
        1500.0
    """
    return micros / 1_000_000


def currency_to_micros(amount: Union[float, int]) -> int:
    """
    Convert currency units to micros.

    Args:
        amount: Amount in currency units

    Returns:
        Amount in micros

    Example:
        >>> currency_to_micros(1500)
        1500000000
    """
    return int(amount * 1_000_000)


def validate_date_format(date_string: str) -> bool:
    """
    Validate date string is in YYYY-MM-DD format.

    Args:
        date_string: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def build_campaign_resource_name(customer_id: str, campaign_id: str) -> str:
    """
    Build campaign resource name.

    Args:
        customer_id: Customer ID (will be formatted)
        campaign_id: Campaign ID

    Returns:
        Full resource name
    """
    formatted_customer_id = format_customer_id(customer_id)
    return f"customers/{formatted_customer_id}/campaigns/{campaign_id}"


def parse_resource_name(resource_name: str) -> dict:
    """
    Parse a resource name into its components.

    Args:
        resource_name: Resource name (e.g., "customers/1234567890/campaigns/9876543210")

    Returns:
        Dictionary with parsed components
    """
    parts = resource_name.split('/')
    if len(parts) < 4:
        raise ValueError(f"Invalid resource name: {resource_name}")

    return {
        'customer_id': parts[1],
        'resource_type': parts[2],
        'resource_id': parts[3]
    }


def sanitize_campaign_name(name: str) -> str:
    """
    Sanitize campaign name to ensure it's valid.

    Args:
        name: Campaign name

    Returns:
        Sanitized campaign name
    """
    # Remove leading/trailing whitespace
    name = name.strip()

    # Ensure it's not empty
    if not name:
        raise ValueError("Campaign name cannot be empty")

    # Ensure it's not too long (Google Ads limit is 255 characters)
    if len(name) > 255:
        name = name[:255]

    return name
