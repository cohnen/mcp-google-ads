# ✅ Phase 5 Complete - Google Merchant Center MCP Server

## 🚀 Phase 5 Summary

Phase 5 adds a **separate MCP server** for Google Merchant Center product management!

### สิ่งที่ทำเสร็จ:

1. ✅ **GMC MCP Server** (`mcp-gmc/gmc_server.py`)
   - 8 comprehensive tools for product management
   - Content API for Shopping v2.1 integration
   - 700+ lines of production-ready code

2. ✅ **Complete Product Lifecycle Management**
   - Insert new products
   - Update prices (regular + sale)
   - Update inventory/availability
   - Manage custom labels for campaign filtering
   - Delete products
   - List and query products

3. ✅ **Performance Max Integration**
   - Custom labels for feed filtering
   - Seamless integration with main Google Ads server
   - Support for merchant_center_id linking

4. ✅ **Documentation** (`mcp-gmc/README.md`)
   - Complete usage examples
   - API reference
   - Troubleshooting guide
   - Integration workflows

---

## 📦 New Files Created

### Files Created:
```
mcp-gmc/gmc_server.py           # 700 lines - GMC MCP server
mcp-gmc/README.md               # Complete documentation
PHASE5_COMPLETE.md              # This file
```

---

## 🎯 Tools Implemented

### 1. List Products
```python
await list_products(
    merchant_id="123456789",
    max_results=50,
    page_token=None  # For pagination
)
```

**Features:**
- Pagination support
- Configurable result limit (1-250)
- Returns product list with details

**Response:**
```json
{
  "resources": [
    {
      "id": "online:en:US:SKU123",
      "title": "Classic Sunglasses",
      "price": {"value": "29.99", "currency": "USD"},
      ...
    }
  ],
  "nextPageToken": "..."
}
```

### 2. Get Product
```python
await get_product(
    merchant_id="123456789",
    product_id="online:en:US:SKU123"
)
```

**Features:**
- Get full product details
- Returns current price, availability, labels
- Useful for checking product status

### 3. Insert Product
```python
await insert_product(
    merchant_id="123456789",
    offer_id="SKU-001",
    title="Classic Sunglasses - Black",
    description="Stylish black sunglasses with UV protection",
    link="https://example.com/products/sunglasses-black",
    image_link="https://example.com/images/sunglasses.jpg",
    price_value=29.99,
    price_currency="USD",
    availability="in stock",
    brand="SEW Eyewear",
    gtin="0123456789012",
    custom_label_0="promo_nov2025",
    custom_label_1="sunglasses"
)
```

**Features:**
- All required and optional fields supported
- Custom labels for campaign filtering
- Multiple image support
- Product identifiers (GTIN, MPN)
- Sale price support

**Required Fields:**
- offer_id, title, description
- link, image_link
- price_value, price_currency
- availability, condition

**Product Identifiers** (at least one):
- brand
- gtin (barcode)
- mpn (Manufacturer Part Number)

### 4. Update Price
```python
await update_price(
    merchant_id="123456789",
    product_id="online:en:US:SKU123",
    price_value=29.99,
    price_currency="USD",
    sale_price_value=19.99,
    sale_price_currency="USD",
    sale_price_effective_date="2025-11-01T00:00Z/2025-11-30T23:59Z"
)
```

**Features:**
- Update regular price
- Set sale price with date range
- Automatic sale period handling
- Returns updated product details

**Use Cases:**
- Flash sales
- Seasonal promotions
- Price adjustments during campaigns

### 5. Update Inventory
```python
await update_inventory(
    merchant_id="123456789",
    product_id="online:en:US:SKU123",
    availability="in stock",
    quantity=100,
    price_value=29.99  # Optional price update
)
```

**Features:**
- Update stock status
- Set available quantity
- Optional price update
- Real-time inventory sync

**Availability Options:**
- `"in stock"` - Available now
- `"out of stock"` - Not available
- `"preorder"` - Available for pre-order
- `"backorder"` - Temporarily out of stock

### 6. Update Custom Labels
```python
await update_custom_labels(
    merchant_id="123456789",
    product_id="online:en:US:SKU123",
    custom_label_0="promo_nov2025",
    custom_label_1="sunglasses",
    custom_label_2="high_margin",
    custom_label_3="bestseller",
    custom_label_4="clearance"
)
```

**Features:**
- Set up to 5 custom labels
- Used for campaign filtering
- Clear labels by setting to empty string
- Essential for Performance Max targeting

**Use Cases:**
- Campaign filtering: `feed_label="promo_nov2025"`
- Product segmentation by category
- Margin-based targeting
- Seasonal product grouping

### 7. Delete Product
```python
await delete_product(
    merchant_id="123456789",
    product_id="online:en:US:SKU123"
)
```

**Features:**
- Remove product from GMC
- Clean deletion
- Returns success confirmation

---

## 🔄 Integration with Performance Max

### Complete Workflow Example

#### Step 1: Upload Products to GMC
```python
# Upload product with custom label
await insert_product(
    merchant_id="123456789",
    offer_id="SUNGLASSES-BLACK-001",
    title="SEW | Classic Sunglasses | Black",
    description="Premium UV protection sunglasses",
    link="https://seweyewear.com/sunglasses/classic-black",
    image_link="https://seweyewear.com/images/sunglasses-black.jpg",
    price_value=1200,  # 1200 THB
    price_currency="THB",
    availability="in stock",
    brand="SEW Eyewear",
    custom_label_0="promo_nov2025",  # 🔑 Campaign filter
    custom_label_1="sunglasses",
    target_country="TH",
    content_language="th"
)
```

#### Step 2: Create Performance Max Campaign
```python
# Create PMax campaign linked to GMC (main server)
await create_pmax_campaign(
    account_id="1234567890",
    campaign_name="SEW | Sunglasses PMax | TH | 2025-11",
    daily_budget_currency=1500,
    target_roas=2.5,
    merchant_center_id="123456789",
    feed_label="promo_nov2025",  # 🔑 Matches custom_label_0
    start_date="2025-11-10",
    status="PAUSED"
)
```

#### Step 3: Run Campaign & Update Products
```python
# Start campaign
await enable_campaign(
    account_id="1234567890",
    campaign_id="9876543210",
    safety_check=True
)

# Update prices during campaign
await update_price(
    merchant_id="123456789",
    product_id="online:th:TH:SUNGLASSES-BLACK-001",
    price_value=1200,
    sale_price_value=999,  # Flash sale!
    sale_price_effective_date="2025-11-15T00:00Z/2025-11-16T23:59Z"
)
```

#### Step 4: Monitor and Adjust
```python
# Update inventory when stock runs low
await update_inventory(
    merchant_id="123456789",
    product_id="online:th:TH:SUNGLASSES-BLACK-001",
    availability="out of stock"
)

# Campaign automatically stops showing this product
```

---

## 📊 Product ID Format

All product IDs follow this format:
```
{channel}:{contentLanguage}:{targetCountry}:{offerId}
```

### Examples:

| Product ID | Channel | Language | Country | Offer ID |
|------------|---------|----------|---------|----------|
| `online:en:US:SKU123` | Online | English | USA | SKU123 |
| `online:th:TH:PROD-001` | Online | Thai | Thailand | PROD-001 |
| `local:en:GB:STORE-123` | Local | English | UK | STORE-123 |

---

## 🔧 Configuration

### MCP Client Setup

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "google-ads": {
      "command": "python",
      "args": ["/path/to/mcp-google-ads/google_ads_server.py"]
    },
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

### OAuth Scope Required

The GMC server requires this additional scope:
```
https://www.googleapis.com/auth/content
```

When you first run the server, you'll be prompted to authorize this scope.

---

## ⚡ API Details

### Base URL
```
https://shoppingcontent.googleapis.com/content/v2.1
```

### Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/{merchantId}/products` | List products |
| GET | `/{merchantId}/products/{productId}` | Get product |
| POST | `/{merchantId}/products` | Insert product |
| PATCH | `/{merchantId}/products/{productId}` | Update product |
| DELETE | `/{merchantId}/products/{productId}` | Delete product |

### Rate Limits

- **Default quota:** 1000 calls/day per project
- **Batch operations:** Up to 1000 products per batch
- **Image size:** Max 16MB per image
- **Title:** 1-150 characters
- **Description:** Max 5000 characters

---

## 🚧 Known Limitations

1. ⚠️ **No batch operations yet** - Updates are single product only
2. ⚠️ **No image upload** - Only image URLs supported (must be publicly accessible)
3. ⚠️ **No product status checks** - Doesn't check GMC diagnostics/issues
4. ⚠️ **No automatic validation** - Relies on API validation

These can be addressed in future enhancements.

---

## 🎯 Use Cases

### 1. E-commerce Automation
```python
# Sync inventory from your database
for product in database.get_products():
    await update_inventory(
        merchant_id="123456789",
        product_id=f"online:en:US:{product.sku}",
        availability="in stock" if product.stock > 0 else "out of stock",
        quantity=product.stock
    )
```

### 2. Dynamic Pricing
```python
# Update prices based on competitor data
for product in products:
    new_price = pricing_algorithm.calculate(product)
    await update_price(
        merchant_id="123456789",
        product_id=product.id,
        price_value=new_price,
        price_currency="USD"
    )
```

### 3. Campaign-Specific Product Sets
```python
# Tag products for Black Friday campaign
black_friday_products = get_promotional_products()
for product in black_friday_products:
    await update_custom_labels(
        merchant_id="123456789",
        product_id=product.id,
        custom_label_0="black_friday_2025",
        custom_label_2="high_discount"
    )

# Create PMax campaign for tagged products
await create_pmax_campaign(
    account_id="1234567890",
    campaign_name="Black Friday PMax",
    merchant_center_id="123456789",
    feed_label="black_friday_2025"
)
```

---

## 🔒 Error Handling

### Success Response
```json
{
  "success": true,
  "product_id": "online:en:US:SKU123",
  "details": { ... }
}
```

### Error Response
```json
{
  "error": "Failed to insert product",
  "message": "Product validation failed: missing GTIN",
  "status_code": 400,
  "type": "ValidationError"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Missing product identifier | No GTIN, MPN, or brand | Add at least one identifier |
| Image not accessible | URL not public or too large | Check image URL and size |
| Invalid product ID | Wrong format | Use `online:en:US:SKU123` format |
| Product not found | ID doesn't exist | Check product exists in GMC |

---

## ✅ Phase 5 Checklist

| Task | Status |
|------|--------|
| Create GMC MCP server | ✅ |
| Implement list_products | ✅ |
| Implement get_product | ✅ |
| Implement insert_product | ✅ |
| Implement update_price | ✅ |
| Implement update_inventory | ✅ |
| Implement update_custom_labels | ✅ |
| Implement delete_product | ✅ |
| OAuth authentication | ✅ |
| Error handling | ✅ |
| Documentation (README) | ✅ |
| Integration examples | ✅ |

**Phase 5 Complete!** 🎉

Ready for Phase 6: GAQL Recipes for Performance Reporting 🚀

---

## 🔗 Resources

### Google Documentation:
- [Content API for Shopping](https://developers.google.com/shopping-content/guides/quickstart)
- [Product Data Specification](https://support.google.com/merchants/answer/7052112)
- [Custom Labels Guide](https://support.google.com/merchants/answer/6324473)
- [Performance Max Integration](https://support.google.com/google-ads/answer/10724482)

### Project Files:
- `mcp-gmc/gmc_server.py` - GMC MCP server implementation
- `mcp-gmc/README.md` - Complete documentation
- `google_ads_server.py` - Main Google Ads MCP server (for PMax campaigns)

---

**Built with ❤️ for huge8888/mcp-google-ads**
