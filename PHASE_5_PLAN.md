# Phase 5 (v1.1): Order Management - Implementation Plan

## Overview

Phase 5 adds order and invoice management to the 3D Filament Scanner application. This allows users to:
- Upload invoices (PDF/image) from filament purchases
- Parse invoice line items automatically
- Map line items to existing Products or create new ones
- Auto-generate Spools with pricing, vendor, and order tracking

## Data Model

### New Entities

#### Order
Represents a purchase order/invoice from a vendor.

**Fields:**
- `id` (int, PK) - Auto-increment primary key
- `vendor` (str, required) - Vendor name (Amazon, Bambu, Micro Center, etc.)
- `order_number` (str, required) - Vendor-specific order ID
- `order_date` (date, optional) - Date of purchase
- `invoice_path` (str, optional) - Path to uploaded invoice file
- `total_amount` (float, optional) - Total order amount
- `currency` (str, default="USD") - Currency code
- `created_at` (datetime) - Record creation timestamp
- `updated_at` (datetime) - Last update timestamp

**Relationships:**
- `items` → List[OrderItem] - Line items in this order
- `spools` → List[Spool] - Spools created from this order

#### OrderItem
Represents a single line item from an invoice.

**Fields:**
- `id` (int, PK) - Auto-increment primary key
- `order_id` (int, FK → Order, required) - Parent order
- `product_id` (int, FK → Product, optional) - Mapped product (null until confirmed)
- `title_raw` (str, required) - Raw line item text from invoice
- `quantity` (int, required) - Number of spools in this line
- `unit_price` (float, required) - Price per spool
- `currency` (str, default="USD") - Currency code
- `status` (enum, required) - `pending_mapping` or `confirmed`
- `created_at` (datetime) - Record creation timestamp
- `updated_at` (datetime) - Last update timestamp

**Relationships:**
- `order` → Order - Parent order
- `product` → Product - Mapped product (optional)

**Status Enum:**
- `pending_mapping` - Line item needs manual Product mapping
- `confirmed` - Mapping confirmed, ready to generate Spools

### Updated Entities

#### Spool
**Changes:**
- `order_id` (int, FK → Order) - Now a proper foreign key (was nullable int)
- Added relationship: `order` → Order

#### Product
**Changes:**
- Added relationship: `order_items` → List[OrderItem]

## API Endpoints

### Order Management

#### `POST /api/v1/orders`
Create a new order with metadata (no invoice upload yet).

**Request:**
```json
{
  "vendor": "Amazon",
  "order_number": "112-1234567-1234567",
  "order_date": "2024-01-15",
  "total_amount": 127.50,
  "currency": "USD"
}
```

**Response:** Order object with `id`

---

#### `GET /api/v1/orders`
List all orders.

**Query Parameters:**
- `vendor` (optional) - Filter by vendor

**Response:** Array of Order objects

---

#### `GET /api/v1/orders/{order_id}`
Get order details including items.

**Response:**
```json
{
  "id": 1,
  "vendor": "Amazon",
  "order_number": "112-1234567-1234567",
  "order_date": "2024-01-15",
  "invoice_path": "/media/invoices/amazon_112-1234567-1234567.pdf",
  "total_amount": 127.50,
  "currency": "USD",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 5,
      "title_raw": "Sunlu PLA+ Yellow 1.75mm 1kg (2-Pack)",
      "quantity": 2,
      "unit_price": 21.99,
      "currency": "USD",
      "status": "confirmed"
    }
  ]
}
```

---

#### `PUT /api/v1/orders/{order_id}`
Update order metadata.

**Request:** Partial Order fields

**Response:** Updated Order object

---

#### `DELETE /api/v1/orders/{order_id}`
Delete an order (cascade deletes items, nullifies Spool.order_id).

**Response:** 204 No Content

---

#### `POST /api/v1/orders/{order_id}/invoice`
Upload and parse an invoice file.

**Request:** Multipart form-data
- `file` - PDF or image file

**Flow:**
1. Save file to `/media/invoices/`
2. Extract text (PDF parser or OCR)
3. Parse line items using vendor-specific parser
4. Create OrderItem records with `status=pending_mapping`
5. Attempt auto-mapping to existing Products
6. Return parsed items with suggestions

**Response:**
```json
{
  "order_id": 1,
  "invoice_path": "/media/invoices/amazon_112-1234567-1234567.pdf",
  "items_parsed": 3,
  "items": [
    {
      "id": 1,
      "title_raw": "Sunlu PLA+ Yellow 1.75mm 1kg",
      "quantity": 2,
      "unit_price": 21.99,
      "suggested_product_id": 5,
      "confidence": "high"
    },
    {
      "id": 2,
      "title_raw": "eSUN PETG Blue 1.75mm 1kg",
      "quantity": 1,
      "unit_price": 25.99,
      "suggested_product_id": null,
      "confidence": "none"
    }
  ]
}
```

---

#### `POST /api/v1/orders/{order_id}/items/{item_id}/map`
Map an OrderItem to a Product.

**Request:**
```json
{
  "product_id": 5,
  "create_new": false
}
```

**OR** (create new product):
```json
{
  "create_new": true,
  "product": {
    "brand": "Sunlu",
    "material": "PLA",
    "color_name": "Yellow",
    "diameter_mm": 1.75
  }
}
```

**Response:** Updated OrderItem with `product_id` set, `status=confirmed`

---

#### `POST /api/v1/orders/{order_id}/confirm`
Confirm all mappings and create Spools for all confirmed OrderItems.

**Request:**
```json
{
  "storage_location": "Shelf A2"
}
```

**Flow:**
1. Check all items have `status=confirmed` and `product_id` set
2. For each item with quantity N:
   - Create N Spool records
   - Set `product_id`, `order_id`, `vendor`, `price=unit_price`
   - Set `status=in_stock`, `storage_location` from request
3. Return count of spools created

**Response:**
```json
{
  "order_id": 1,
  "spools_created": 5,
  "spool_ids": [12, 13, 14, 15, 16]
}
```

---

### OrderItem Management

#### `GET /api/v1/order-items`
List all order items (for debugging).

**Query Parameters:**
- `status` (optional) - Filter by status

**Response:** Array of OrderItem objects

---

#### `GET /api/v1/order-items/{item_id}`
Get specific order item.

**Response:** OrderItem object

---

#### `PUT /api/v1/order-items/{item_id}`
Update order item (for manual corrections).

**Request:** Partial OrderItem fields

**Response:** Updated OrderItem object

---

#### `DELETE /api/v1/order-items/{item_id}`
Delete an order item.

**Response:** 204 No Content

---

## Invoice Parsing Pipeline

### Architecture

```
Invoice Upload → Text Extraction → Vendor Detection → Line Parsing → Product Matching
```

### Text Extraction

**PDF Files:**
- Use `PyPDF2` or `pdfplumber` library
- Extract all text pages
- Preserve structure for line parsing

**Image Files:**
- Use Tesseract OCR via `pytesseract`
- Pre-process: grayscale, threshold, deskew
- Extract text

### Vendor Detection

Identify vendor from:
1. Order metadata (if provided)
2. Invoice text patterns:
   - "Amazon.com" → Amazon
   - "bambulab.com" → Bambu
   - "Micro Center" → Micro Center

### Line Item Parsing

**Parser Interface:**
```python
class InvoiceParser:
    def parse_lines(self, text: str) -> List[Dict]:
        """
        Returns list of:
        {
            "title_raw": str,
            "quantity": int,
            "unit_price": float,
            "currency": str
        }
        """
```

**Vendor-Specific Parsers:**

#### Amazon Parser
- Look for product title + quantity pattern
- Extract price from "Price: $XX.XX" or similar
- Handle multi-packs: "Sunlu PLA (2-Pack)" → quantity=2

#### Bambu Parser
- Parse structured line items
- Look for material + color + weight
- Extract SKU if available

#### Generic Parser (Fallback)
- Regex patterns for common formats
- Keywords: PLA, PETG, TPU, 1.75mm, kg
- Extract quantities and prices

### Product Matching

**Matching Strategy:**

1. **Exact Match:**
   - Extract: brand, material, color, diameter from `title_raw`
   - Query Products: `brand=X AND material=Y AND color_name=Z AND diameter_mm=D`
   - If single match → confidence="high"

2. **Partial Match:**
   - Match on brand + material only
   - If 1-3 matches → confidence="medium", suggest first
   - If >3 matches → confidence="low"

3. **No Match:**
   - confidence="none"
   - User must create new Product or map manually

**Extraction Functions:**
```python
def extract_brand(title: str) -> Optional[str]:
    """Match against known brands: Sunlu, eSUN, Bambu, etc."""

def extract_material(title: str) -> Optional[str]:
    """Match: PLA, PLA+, PETG, TPU, ABS, etc."""

def extract_color(title: str) -> Optional[str]:
    """Match color keywords"""

def extract_diameter(title: str) -> float:
    """Match: 1.75mm, 2.85mm, etc."""
```

---

## Frontend UI

### New Pages

#### OrderListPage (`/orders`)
- Table view of all orders
- Columns: Order Number, Vendor, Date, Total, Status, Actions
- Filter by vendor, date range
- "New Order" button → create modal

#### OrderDetailPage (`/orders/:id`)
**Sections:**
1. **Order Info** - Vendor, order number, date, total, invoice link
2. **Invoice Upload** - If no invoice yet, show upload form
3. **Line Items Table:**
   - Columns: Title Raw, Quantity, Unit Price, Mapped Product, Status, Actions
   - Actions: "Map to Product" button (if pending)
4. **Mapping UI:**
   - For each pending item: dropdown to select existing Product
   - "Create New Product" button → inline form
5. **Confirm Order** - Button to create Spools (enabled when all items confirmed)

#### Product Mapping Modal
- Show suggested products with confidence
- Dropdown to select from all Products
- "Create New" form:
  - Brand, Material, Color, Diameter (pre-filled from parsing)
  - Line, Notes, Barcode, SKU

---

## Implementation Tasks

### Backend

#### Models ✅ (Completed)
- [x] Add `Order` model
- [x] Add `OrderItem` model
- [x] Update `Spool.order_id` to foreign key
- [x] Add relationships

#### API Endpoints
- [ ] `POST /api/v1/orders`
- [ ] `GET /api/v1/orders`
- [ ] `GET /api/v1/orders/{id}`
- [ ] `PUT /api/v1/orders/{id}`
- [ ] `DELETE /api/v1/orders/{id}`
- [ ] `POST /api/v1/orders/{id}/invoice` (file upload + parsing)
- [ ] `POST /api/v1/orders/{id}/items/{item_id}/map`
- [ ] `POST /api/v1/orders/{id}/confirm`
- [ ] `GET /api/v1/order-items`
- [ ] `GET /api/v1/order-items/{id}`
- [ ] `PUT /api/v1/order-items/{id}`
- [ ] `DELETE /api/v1/order-items/{id}`

#### Invoice Parsing
- [ ] Add dependencies: `pdfplumber`, `pytesseract`, `Pillow`
- [ ] Implement text extraction (PDF + OCR)
- [ ] Create `InvoiceParser` base class
- [ ] Implement `AmazonParser`
- [ ] Implement `BambuParser`
- [ ] Implement `GenericParser` (fallback)
- [ ] Create product matching logic
- [ ] Add unit tests with sample invoices

#### File Storage
- [ ] Create `/media/invoices/` directory
- [ ] Implement file upload handling
- [ ] Add file validation (PDF, PNG, JPG only, max 10MB)

### Frontend

#### Pages
- [ ] `OrderListPage` - List all orders
- [ ] `OrderDetailPage` - Order details + mapping UI
- [ ] `OrderCreateModal` - Create new order

#### Components
- [ ] `InvoiceUploader` - Drag-and-drop file upload
- [ ] `LineItemMapper` - Map item to product
- [ ] `ProductMatchSuggestions` - Show matching products
- [ ] `CreateProductForm` - Inline product creation

#### API Integration
- [ ] Order CRUD operations
- [ ] Invoice upload with progress bar
- [ ] Product mapping actions
- [ ] Order confirmation flow

### Testing

#### Backend Tests
- [ ] Order CRUD endpoints
- [ ] OrderItem CRUD endpoints
- [ ] Invoice upload and parsing (mocked files)
- [ ] Product matching logic
- [ ] Spool creation from order confirmation
- [ ] Foreign key constraints

#### Frontend Tests
- [ ] Order list rendering
- [ ] Order detail page
- [ ] Invoice upload
- [ ] Product mapping workflow
- [ ] Error handling

### Documentation
- [x] Phase 5 implementation plan (this document)
- [ ] API endpoint documentation in Swagger
- [ ] Invoice parser development guide
- [ ] User guide for order workflow

---

## Development Workflow

### Phase 5.1: Order CRUD (No Parsing)
1. Implement Order and OrderItem models ✅
2. Add basic CRUD endpoints
3. Create frontend pages for manual order entry
4. Test with manual data entry

### Phase 5.2: Invoice Parsing
1. Add file upload endpoint
2. Implement text extraction (PDF + OCR)
3. Create vendor-specific parsers
4. Test with real invoices from each vendor

### Phase 5.3: Product Mapping
1. Implement matching algorithm
2. Add mapping endpoints
3. Create mapping UI
4. Test end-to-end workflow

### Phase 5.4: Spool Generation
1. Implement confirmation endpoint
2. Add batch Spool creation
3. Test spool generation
4. Add frontend integration

---

## Sample Workflow

### User Journey: Import Amazon Order

1. **Create Order:**
   - User clicks "New Order" → fills vendor="Amazon", order_number
   - POST /api/v1/orders → order created

2. **Upload Invoice:**
   - User drags PDF invoice to upload area
   - POST /api/v1/orders/1/invoice → parsing begins
   - Backend extracts text, parses 3 line items
   - Returns items with auto-matched products

3. **Review Mappings:**
   - Item 1: "Sunlu PLA+ Yellow" → Auto-mapped to Product #5 (high confidence) ✅
   - Item 2: "eSUN PETG Blue" → Auto-mapped to Product #8 (medium confidence) ⚠️
   - Item 3: "Generic TPU Red" → No match ❌

4. **Adjust Mappings:**
   - User confirms Item 1 (already correct)
   - User changes Item 2 to Product #9 (correct eSUN product)
   - User clicks "Create New Product" for Item 3 → fills brand="eSUN", material="TPU", color="Red"

5. **Confirm Order:**
   - All items now have `status=confirmed`
   - User sets `storage_location="Shelf A2"`
   - Clicks "Confirm & Create Spools"
   - POST /api/v1/orders/1/confirm → 5 spools created

6. **View Results:**
   - Redirected to Spools page
   - Sees 5 new spools with correct product, vendor, price, and order linkage

---

## Dependencies

### Python Packages (add to requirements.txt)
```
pdfplumber>=0.10.0
pytesseract>=0.3.10
Pillow>=10.0.0
python-multipart>=0.0.6  # for file uploads
```

### System Dependencies (for Docker)
```dockerfile
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng
```

---

## Database Migration Strategy

Since SQLModel uses SQLAlchemy, consider using Alembic for migrations:

1. Install Alembic: `pip install alembic`
2. Initialize: `alembic init alembic`
3. Configure `alembic.ini` to use SQLModel metadata
4. Generate migration:
   ```bash
   alembic revision --autogenerate -m "Add Order and OrderItem models"
   ```
5. Apply migration:
   ```bash
   alembic upgrade head
   ```

**Or** use SQLModel's `create_all()` for simple cases (current approach).

---

## Future Enhancements (Not in Phase 5)

- AI-powered invoice parsing (GPT-4 Vision for receipt images)
- Barcode scanning from invoice PDFs
- Multi-currency support with exchange rates
- Order analytics (spending by vendor, price trends)
- Duplicate order detection
- Import from CSV/Excel
- Webhook integration with vendor APIs

---

## Notes

- Phase 5 models are already added to `backend/models.py` ✅
- All relationships and foreign keys are properly defined ✅
- The Spool table already had `order_id`, now properly linked ✅
- Frontend pages from Phase 2 don't yet include Order management
- Invoice parsing is the most complex part - start with simple manual entry
- Consider adding sample invoices to `tests/fixtures/` for testing parsers
