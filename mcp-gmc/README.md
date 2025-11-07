# Google Merchant Center MCP Server

MCP server for managing products in Google Merchant Center via Content API for Shopping v2.1.

## Features

### Product Management Tools

1. **`list_products`** - List all products in your GMC account
2. **`get_product`** - Get details of a specific product
3. **`insert_product`** - Add a new product to GMC
4. **`update_price`** - Update product pricing (regular and sale prices)
5. **`update_inventory`** - Update stock availability and quantity
6. **`update_custom_labels`** - Set custom labels for campaign filtering
7. **`delete_product`** - Remove a product from GMC

## Setup

### 1. Authentication

The GMC server uses the same OAuth2 credentials as the main Google Ads server:

```bash
# Set environment variables (in parent directory .env)
GOOGLE_ADS_CLIENT_SECRET_PATH=/path/to/client_secret.json
GOOGLE_ADS_TOKEN_PATH=/path/to/token.pickle
```

**Required OAuth Scope:**
- `https://www.googleapis.com/auth/content`

### 2. Running the Server

```bash
# From the mcp-gmc directory
python gmc_server.py
```

Or use with MCP client configuration:

```json
{
  "mcpServers": {
    "google-merchant-center": {
      "command": "python",
      "args": ["/path/to/mcp-google-ads/mcp-gmc/gmc_server.py"],
      "env": {
        "GOOGLE_ADS_CLIENT_SECRET_PATH": "/path/to/client_secret.json",
        "GOOGLE_ADS_TOKEN_PATH": "/path/to/token.pickle"
      }
    }
  }
}
```

## Usage Examples

### List Products

```python
# List first 50 products
result = await list_products(
    merchant_id="123456789",
    max_results=50
)
```

### Insert New Product

```python
result = await insert_product(
    merchant_id="123456789",
    offer_id="SKU-SUNGLASSES-001",
    title="Classic Sunglasses - Black",
    description="Stylish black sunglasses with UV protection",
    link="https://example.com/products/sunglasses-black",
    image_link="https://example.com/images/sunglasses-black.jpg",
    price_value=29.99,
    price_currency="USD",
    availability="in stock",
    brand="SEW Eyewear",
    custom_label_0="promo_nov2025",  # For campaign filtering
    custom_label_1="sunglasses",
    custom_label_2="high_margin"
)
```

### Update Price (with Sale)

```python
result = await update_price(
    merchant_id="123456789",
    product_id="online:en:US:SKU-SUNGLASSES-001",
    price_value=29.99,
    price_currency="USD",
    sale_price_value=19.99,
    sale_price_effective_date="2025-11-01T00:00Z/2025-11-30T23:59Z"
)
```

### Update Inventory

```python
result = await update_inventory(
    merchant_id="123456789",
    product_id="online:en:US:SKU-SUNGLASSES-001",
    availability="out of stock"
)
```

### Update Custom Labels (for Campaign Filtering)

Custom labels are used in Performance Max campaigns to filter which products to show:

```python
result = await update_custom_labels(
    merchant_id="123456789",
    product_id="online:en:US:SKU-SUNGLASSES-001",
    custom_label_0="promo_nov2025",  # Match this in PMax campaign
    custom_label_1="sunglasses",
    custom_label_2="high_margin"
)
```

Then in your Performance Max campaign, use `feed_label="promo_nov2025"` to only show products with this label.

## Product ID Format

Product IDs in GMC follow this format:
```
{channel}:{contentLanguage}:{targetCountry}:{offerId}
```

Examples:
- `online:en:US:SKU123` - Online product, English, USA, SKU "SKU123"
- `online:th:TH:PROD-001` - Online product, Thai, Thailand, SKU "PROD-001"
- `local:en:GB:STORE-123` - Local product, English, UK, SKU "STORE-123"

## Integration with Performance Max Campaigns

This GMC server works seamlessly with the main Google Ads MCP server:

### Workflow Example

1. **Upload products to GMC** (this server):
   ```python
   await insert_product(
       merchant_id="123456789",
       offer_id="SKU-001",
       custom_label_0="promo_nov2025",
       ...
   )
   ```

2. **Create Performance Max campaign** (main server):
   ```python
   await create_pmax_campaign(
       account_id="1234567890",
       campaign_name="Sunglasses PMax",
       merchant_center_id="123456789",
       feed_label="promo_nov2025",  # Matches custom_label_0
       ...
   )
   ```

3. **Update product prices during campaign**:
   ```python
   await update_price(
       merchant_id="123456789",
       product_id="online:en:US:SKU-001",
       sale_price_value=19.99
   )
   ```

## API Reference

### Content API for Shopping v2.1

Base URL: `https://shoppingcontent.googleapis.com/content/v2.1`

**Endpoints used:**
- `GET /{merchantId}/products` - List products
- `GET /{merchantId}/products/{productId}` - Get product
- `POST /{merchantId}/products` - Insert product
- `PATCH /{merchantId}/products/{productId}` - Update product
- `DELETE /{merchantId}/products/{productId}` - Delete product

## Product Requirements

### Required Fields

For all products:
- `offerId` - Unique identifier (SKU)
- `title` - Product title (1-150 chars)
- `description` - Product description (max 5000 chars)
- `link` - Landing page URL
- `imageLink` - Main image URL
- `contentLanguage` - Language (ISO 639-1)
- `targetCountry` - Country (ISO 3166-1 alpha-2)
- `channel` - "online" or "local"
- `availability` - Stock status
- `condition` - "new", "refurbished", or "used"
- `price` - Price with currency

### Product Identifiers

At least one of:
- `gtin` - Global Trade Item Number (barcode)
- `mpn` - Manufacturer Part Number
- `brand` - Brand name

### Optional Fields

- `salePrice` - Sale price
- `salePriceEffectiveDate` - Sale period
- `googleProductCategory` - Google's category taxonomy
- `productType` - Your custom category
- `customLabel0-4` - Custom labels (max 1000 chars each)
- `additionalImageLinks` - Up to 10 additional images

## Error Handling

All tools return JSON responses:

**Success:**
```json
{
  "success": true,
  "product_id": "online:en:US:SKU123",
  "details": { ... }
}
```

**Error:**
```json
{
  "error": "Failed to insert product",
  "message": "Product validation failed: missing GTIN",
  "status_code": 400
}
```

## Troubleshooting

### Common Issues

**1. Authentication Error**
```
Error: invalid_grant
```
Solution: Delete `token.pickle` and re-authenticate

**2. Product Validation Error**
```
Error: Missing required product identifier
```
Solution: Add at least one of: `gtin`, `mpn`, or `brand`

**3. Image Not Crawlable**
```
Error: Image link is not accessible
```
Solution: Ensure image URL is publicly accessible and < 16MB

**4. Invalid Product ID**
```
Error: Product not found
```
Solution: Check product ID format: `online:en:US:SKU123`

## Limits and Quotas

- **Products per account:** Varies by GMC plan
- **API calls:** 1000 calls per day per project (default)
- **Batch size:** Up to 1000 products per batch request
- **Image size:** Max 16MB per image
- **Title length:** 1-150 characters
- **Description length:** Max 5000 characters

## Next Steps

- Add batch operations for bulk updates
- Implement product status monitoring
- Add image upload helper
- Create product validation tool
- Add GMC diagnostics integration

## Related Documentation

- [Content API for Shopping](https://developers.google.com/shopping-content/guides/quickstart)
- [Product Data Specification](https://support.google.com/merchants/answer/7052112)
- [Custom Labels Guide](https://support.google.com/merchants/answer/6324473)
- [Performance Max Integration](https://support.google.com/google-ads/answer/10724482)
