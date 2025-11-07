#!/usr/bin/env python3
"""
Google Merchant Center MCP Server
Provides tools for managing products via Content API for Shopping v2.1
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from pydantic import Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Google Merchant Center", dependencies=["google-auth", "google-auth-oauthlib", "requests"])

# API Configuration
API_VERSION = "v2.1"
GMC_BASE_URL = f"https://shoppingcontent.googleapis.com/content/{API_VERSION}"

# Authentication helpers (reuse from google_ads_server.py)
def get_credentials():
    """Get Google OAuth2 credentials"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    import os
    import pickle

    SCOPES = ['https://www.googleapis.com/auth/content']

    creds = None
    token_path = os.environ.get('GOOGLE_ADS_TOKEN_PATH', 'token.pickle')

    # Load existing token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            logger.info("Getting new credentials via OAuth flow...")
            client_config_path = os.environ.get('GOOGLE_ADS_CLIENT_SECRET_PATH', 'client_secret.json')
            flow = InstalledAppFlow.from_client_secrets_file(client_config_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_headers(credentials) -> Dict[str, str]:
    """Get HTTP headers with access token"""
    return {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json"
    }


@mcp.tool()
async def list_products(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    max_results: int = Field(default=50, description="Maximum number of products to return (max 250)"),
    page_token: str = Field(default=None, description="Token for pagination")
) -> str:
    """
    List products in Google Merchant Center account.

    Args:
        merchant_id: Merchant Center account ID
        max_results: Maximum results per page (1-250)
        page_token: Pagination token from previous request

    Returns:
        JSON with list of products

    Example:
        merchant_id: "123456789"
        max_results: 50
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        # Build URL
        url = f"{GMC_BASE_URL}/{merchant_id}/products"

        # Add query parameters
        params = {"maxResults": min(max_results, 250)}
        if page_token:
            params["pageToken"] = page_token

        logger.info(f"Listing products for merchant {merchant_id}")

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            error_msg = f"Failed to list products: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to list products",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()

        product_count = len(result.get('resources', []))
        logger.info(f"Retrieved {product_count} products")

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error in list_products: {str(e)}")
        return json.dumps({
            "error": "Failed to list products",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def get_product(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    product_id: str = Field(description="Product ID (format: online:en:US:SKU123)")
) -> str:
    """
    Get a single product from Google Merchant Center.

    Args:
        merchant_id: Merchant Center account ID
        product_id: Product ID in format "online:language:country:offerId"

    Returns:
        JSON with product details

    Example:
        merchant_id: "123456789"
        product_id: "online:en:US:SKU123"
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        url = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"

        logger.info(f"Getting product {product_id} from merchant {merchant_id}")

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            error_msg = f"Failed to get product: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to get product",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()
        logger.info(f"Retrieved product: {result.get('title', 'Unknown')}")

        return json.dumps(result, indent=2)

    except Exception as e:
        logger.error(f"Error in get_product: {str(e)}")
        return json.dumps({
            "error": "Failed to get product",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def insert_product(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    offer_id: str = Field(description="Unique offer ID (SKU)"),
    title: str = Field(description="Product title"),
    description: str = Field(description="Product description"),
    link: str = Field(description="Product landing page URL"),
    image_link: str = Field(description="Main product image URL"),
    price_value: float = Field(description="Product price value"),
    price_currency: str = Field(default="USD", description="Price currency (ISO 4217)"),
    availability: str = Field(default="in stock", description="Availability: 'in stock', 'out of stock', 'preorder'"),
    condition: str = Field(default="new", description="Product condition: 'new', 'refurbished', 'used'"),
    brand: str = Field(default=None, description="Brand name"),
    gtin: str = Field(default=None, description="GTIN (barcode)"),
    mpn: str = Field(default=None, description="Manufacturer Part Number"),
    google_product_category: str = Field(default=None, description="Google product category ID"),
    product_type: str = Field(default=None, description="Product type (custom category)"),
    target_country: str = Field(default="US", description="Target country (ISO 3166-1 alpha-2)"),
    content_language: str = Field(default="en", description="Content language (ISO 639-1)"),
    channel: str = Field(default="online", description="Channel: 'online' or 'local'"),
    custom_label_0: str = Field(default=None, description="Custom label 0 (for filtering in campaigns)"),
    custom_label_1: str = Field(default=None, description="Custom label 1"),
    custom_label_2: str = Field(default=None, description="Custom label 2"),
    custom_label_3: str = Field(default=None, description="Custom label 3"),
    custom_label_4: str = Field(default=None, description="Custom label 4"),
    additional_image_links: List[str] = Field(default=None, description="Additional product images")
) -> str:
    """
    Insert a new product into Google Merchant Center.

    Args:
        merchant_id: Merchant Center account ID
        offer_id: Unique identifier (SKU)
        title: Product title
        description: Product description
        link: Landing page URL
        image_link: Main image URL
        price_value: Price (numeric)
        price_currency: Currency code
        availability: Stock status
        condition: Product condition
        brand: Brand name
        gtin: GTIN/barcode
        mpn: Manufacturer Part Number
        google_product_category: Google category
        product_type: Custom product type
        target_country: Country code
        content_language: Language code
        channel: Sales channel
        custom_label_0-4: Custom labels for campaign filtering
        additional_image_links: List of additional image URLs

    Returns:
        JSON with created product details

    Example:
        merchant_id: "123456789"
        offer_id: "SKU123"
        title: "Classic Sunglasses - Black"
        description: "Stylish black sunglasses with UV protection"
        link: "https://example.com/products/sunglasses-black"
        image_link: "https://example.com/images/sunglasses-black.jpg"
        price_value: 29.99
        price_currency: "USD"
        availability: "in stock"
        brand: "SEW Eyewear"
        custom_label_0: "promo_nov2025"
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        # Build product data
        product = {
            "offerId": offer_id,
            "title": title,
            "description": description,
            "link": link,
            "imageLink": image_link,
            "contentLanguage": content_language,
            "targetCountry": target_country,
            "channel": channel,
            "availability": availability,
            "condition": condition,
            "price": {
                "value": str(price_value),
                "currency": price_currency
            }
        }

        # Add optional fields
        if brand:
            product["brand"] = brand
        if gtin:
            product["gtin"] = gtin
        if mpn:
            product["mpn"] = mpn
        if google_product_category:
            product["googleProductCategory"] = google_product_category
        if product_type:
            product["productType"] = product_type
        if custom_label_0:
            product["customLabel0"] = custom_label_0
        if custom_label_1:
            product["customLabel1"] = custom_label_1
        if custom_label_2:
            product["customLabel2"] = custom_label_2
        if custom_label_3:
            product["customLabel3"] = custom_label_3
        if custom_label_4:
            product["customLabel4"] = custom_label_4
        if additional_image_links:
            product["additionalImageLinks"] = additional_image_links

        url = f"{GMC_BASE_URL}/{merchant_id}/products"

        logger.info(f"Inserting product: {title}")
        logger.debug(f"Product data: {json.dumps(product, indent=2)}")

        response = requests.post(url, headers=headers, json=product)

        if response.status_code not in [200, 201]:
            error_msg = f"Failed to insert product: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to insert product",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()
        logger.info(f"Successfully inserted product: {offer_id}")

        return json.dumps({
            "success": True,
            "product_id": result.get("id"),
            "offer_id": offer_id,
            "title": title,
            "details": result
        }, indent=2)

    except Exception as e:
        logger.error(f"Error in insert_product: {str(e)}")
        return json.dumps({
            "error": "Failed to insert product",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def update_price(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    product_id: str = Field(description="Product ID (format: online:en:US:SKU123)"),
    price_value: float = Field(description="New price value"),
    price_currency: str = Field(default="USD", description="Price currency (ISO 4217)"),
    sale_price_value: float = Field(default=None, description="Sale price value (optional)"),
    sale_price_currency: str = Field(default=None, description="Sale price currency"),
    sale_price_effective_date: str = Field(default=None, description="Sale period (e.g., '2025-11-01T00:00Z/2025-11-30T23:59Z')")
) -> str:
    """
    Update product price in Google Merchant Center.

    Args:
        merchant_id: Merchant Center account ID
        product_id: Product ID in format "online:language:country:offerId"
        price_value: New regular price
        price_currency: Currency code
        sale_price_value: Optional sale price
        sale_price_currency: Sale price currency
        sale_price_effective_date: Sale period in ISO 8601 interval format

    Returns:
        JSON with update status

    Example:
        merchant_id: "123456789"
        product_id: "online:en:US:SKU123"
        price_value: 24.99
        sale_price_value: 19.99
        sale_price_effective_date: "2025-11-01T00:00Z/2025-11-30T23:59Z"
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        # First get current product
        url_get = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"
        response_get = requests.get(url_get, headers=headers)

        if response_get.status_code != 200:
            return json.dumps({
                "error": "Failed to get product",
                "message": response_get.text
            }, indent=2)

        product = response_get.json()

        # Update price
        product["price"] = {
            "value": str(price_value),
            "currency": price_currency
        }

        # Add sale price if provided
        if sale_price_value is not None:
            product["salePrice"] = {
                "value": str(sale_price_value),
                "currency": sale_price_currency or price_currency
            }
            if sale_price_effective_date:
                product["salePriceEffectiveDate"] = sale_price_effective_date

        # Update product
        url_update = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"

        logger.info(f"Updating price for product {product_id}")

        response = requests.patch(url_update, headers=headers, json=product)

        if response.status_code != 200:
            error_msg = f"Failed to update price: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to update price",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()
        logger.info(f"Successfully updated price for {product_id}")

        return json.dumps({
            "success": True,
            "product_id": product_id,
            "new_price": f"{price_value} {price_currency}",
            "sale_price": f"{sale_price_value} {sale_price_currency or price_currency}" if sale_price_value else None,
            "details": result
        }, indent=2)

    except Exception as e:
        logger.error(f"Error in update_price: {str(e)}")
        return json.dumps({
            "error": "Failed to update price",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def update_inventory(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    product_id: str = Field(description="Product ID (format: online:en:US:SKU123)"),
    availability: str = Field(description="Availability: 'in stock', 'out of stock', 'preorder', 'backorder'"),
    quantity: int = Field(default=None, description="Available quantity (optional)"),
    price_value: float = Field(default=None, description="Updated price (optional)"),
    price_currency: str = Field(default=None, description="Price currency (optional)")
) -> str:
    """
    Update product inventory/availability in Google Merchant Center.

    Args:
        merchant_id: Merchant Center account ID
        product_id: Product ID in format "online:language:country:offerId"
        availability: Stock status
        quantity: Available quantity
        price_value: Optional price update
        price_currency: Currency for price update

    Returns:
        JSON with update status

    Example:
        merchant_id: "123456789"
        product_id: "online:en:US:SKU123"
        availability: "in stock"
        quantity: 100
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        # Get current product
        url_get = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"
        response_get = requests.get(url_get, headers=headers)

        if response_get.status_code != 200:
            return json.dumps({
                "error": "Failed to get product",
                "message": response_get.text
            }, indent=2)

        product = response_get.json()

        # Update availability
        product["availability"] = availability

        if quantity is not None:
            product["quantity"] = quantity

        # Update price if provided
        if price_value is not None and price_currency:
            product["price"] = {
                "value": str(price_value),
                "currency": price_currency
            }

        # Update product
        url_update = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"

        logger.info(f"Updating inventory for product {product_id}")

        response = requests.patch(url_update, headers=headers, json=product)

        if response.status_code != 200:
            error_msg = f"Failed to update inventory: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to update inventory",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()
        logger.info(f"Successfully updated inventory for {product_id}")

        return json.dumps({
            "success": True,
            "product_id": product_id,
            "availability": availability,
            "quantity": quantity,
            "details": result
        }, indent=2)

    except Exception as e:
        logger.error(f"Error in update_inventory: {str(e)}")
        return json.dumps({
            "error": "Failed to update inventory",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def update_custom_labels(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    product_id: str = Field(description="Product ID (format: online:en:US:SKU123)"),
    custom_label_0: str = Field(default=None, description="Custom label 0"),
    custom_label_1: str = Field(default=None, description="Custom label 1"),
    custom_label_2: str = Field(default=None, description="Custom label 2"),
    custom_label_3: str = Field(default=None, description="Custom label 3"),
    custom_label_4: str = Field(default=None, description="Custom label 4")
) -> str:
    """
    Update custom labels for a product (used for campaign filtering).

    Args:
        merchant_id: Merchant Center account ID
        product_id: Product ID in format "online:language:country:offerId"
        custom_label_0-4: Custom labels (set to empty string to clear)

    Returns:
        JSON with update status

    Example:
        merchant_id: "123456789"
        product_id: "online:en:US:SKU123"
        custom_label_0: "promo_nov2025"
        custom_label_1: "sunglasses"
        custom_label_2: "high_margin"
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        # Get current product
        url_get = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"
        response_get = requests.get(url_get, headers=headers)

        if response_get.status_code != 200:
            return json.dumps({
                "error": "Failed to get product",
                "message": response_get.text
            }, indent=2)

        product = response_get.json()

        # Update custom labels
        if custom_label_0 is not None:
            product["customLabel0"] = custom_label_0
        if custom_label_1 is not None:
            product["customLabel1"] = custom_label_1
        if custom_label_2 is not None:
            product["customLabel2"] = custom_label_2
        if custom_label_3 is not None:
            product["customLabel3"] = custom_label_3
        if custom_label_4 is not None:
            product["customLabel4"] = custom_label_4

        # Update product
        url_update = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"

        logger.info(f"Updating custom labels for product {product_id}")

        response = requests.patch(url_update, headers=headers, json=product)

        if response.status_code != 200:
            error_msg = f"Failed to update custom labels: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to update custom labels",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        result = response.json()
        logger.info(f"Successfully updated custom labels for {product_id}")

        return json.dumps({
            "success": True,
            "product_id": product_id,
            "custom_labels": {
                "label_0": custom_label_0,
                "label_1": custom_label_1,
                "label_2": custom_label_2,
                "label_3": custom_label_3,
                "label_4": custom_label_4
            },
            "details": result
        }, indent=2)

    except Exception as e:
        logger.error(f"Error in update_custom_labels: {str(e)}")
        return json.dumps({
            "error": "Failed to update custom labels",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


@mcp.tool()
async def delete_product(
    merchant_id: str = Field(description="Google Merchant Center account ID"),
    product_id: str = Field(description="Product ID (format: online:en:US:SKU123)")
) -> str:
    """
    Delete a product from Google Merchant Center.

    Args:
        merchant_id: Merchant Center account ID
        product_id: Product ID in format "online:language:country:offerId"

    Returns:
        JSON with deletion status

    Example:
        merchant_id: "123456789"
        product_id: "online:en:US:SKU123"
    """
    try:
        import requests

        creds = get_credentials()
        headers = get_headers(creds)

        url = f"{GMC_BASE_URL}/{merchant_id}/products/{product_id}"

        logger.info(f"Deleting product {product_id}")

        response = requests.delete(url, headers=headers)

        if response.status_code not in [200, 204]:
            error_msg = f"Failed to delete product: {response.text}"
            logger.error(error_msg)
            return json.dumps({
                "error": "Failed to delete product",
                "message": response.text,
                "status_code": response.status_code
            }, indent=2)

        logger.info(f"Successfully deleted product {product_id}")

        return json.dumps({
            "success": True,
            "product_id": product_id,
            "message": "Product deleted successfully"
        }, indent=2)

    except Exception as e:
        logger.error(f"Error in delete_product: {str(e)}")
        return json.dumps({
            "error": "Failed to delete product",
            "message": str(e),
            "type": type(e).__name__
        }, indent=2)


if __name__ == "__main__":
    # Start the MCP server on stdio transport
    mcp.run(transport="stdio")
