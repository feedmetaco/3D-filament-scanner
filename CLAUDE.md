# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

3D Filament Scanner is a local-first web application for cataloging and managing 3D printing filament inventory. It allows users to scan box labels to extract filament information (brand, material, color, etc.) and track individual spools with purchase details and storage locations. The app is designed to be self-hosted on a Synology NAS using Docker and SQLite.

**Primary source of truth**: `README.md` (PROJECT_PLAN.md) - this document defines the complete architecture, data model, and implementation phases. Always consult it before making structural changes.

## Current Implementation Status

**Completed:**
- ✅ Phase 1: v1 Backend (Products & Spools CRUD API) - **100% COMPLETE**
  - ✅ Query filtering (brand, material, color, status, vendor, location)
  - ✅ `POST /api/v1/spools/{id}/mark-used` quick action endpoint
  - ✅ All 8 tests passing
- ✅ Phase 2: v1 Frontend (React UI) - **COMPLETE**
  - ✅ React + Vite + React Router
  - ✅ 4 functional pages (Inventory, Spools, Product Detail, Add Spool)
  - ✅ Mobile-responsive design with dark theme
  - ✅ Full API integration
- ✅ Phase 5 Models: Order & OrderItem database models added
- ✅ Automated testing with pytest
- ✅ GitHub Actions CI pipeline

**Not yet implemented:**
- ⏳ Phase 3: OCR/label scanning functionality
- ⏳ Phase 4: Docker deployment configuration
- ⏳ Phase 5 Implementation: Order management API endpoints & UI (models ready, see PHASE_5_PLAN.md)

## Technology Stack

**Backend:**
- Python 3.11+
- FastAPI (v0.110.0+) for REST API
- SQLModel for ORM (combines SQLAlchemy + Pydantic)
- SQLite for database (file-based: `backend/app.db`)
- Uvicorn ASGI server
- pytest + httpx for testing

**Frontend:**
- React 18 with Vite build system
- React Router v6 for client-side routing
- Vanilla CSS (mobile-responsive, dark theme)
- Located in `frontend/` directory

**Deployment (Planned):**
- Docker + docker-compose
- Target: Synology NAS (local network)

## Common Commands

### Backend Development

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run development server (with auto-reload)
python backend/main.py
# OR
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# Navigate to: http://localhost:8000/docs
```

### Frontend Development

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (with hot reload)
npm run dev
# App available at: http://localhost:5173

# Build for production
npm run build
# Output in: frontend/dist/
```

### Testing

```bash
# Run all backend tests from project root
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py

# Run specific test function
pytest tests/test_api.py::test_filter_products_by_brand
```

### Database

The SQLite database is automatically created at `backend/app.db` on first startup. Database initialization happens via `init_db()` called in the FastAPI startup event (backend/main.py:20-22).

**Environment variable:**
- `DATABASE_URL` - Override default SQLite path (defaults to `sqlite:///./backend/app.db`)

## Architecture

### Data Model

**v1 Entities (Implemented):**

**Product** (`backend/models.py:26-38`)
- Represents a unique filament type (e.g., "Sunlu PLA Yellow 1.75mm")
- Core fields: `brand`, `material`, `color_name`, `diameter_mm`
- Optional fields: `line` (product line), `notes`, `barcode`, `sku`
- **Weight is implicitly 1kg per spool, not stored in database**
- Relationships: One-to-many with Spools, One-to-many with OrderItems

**Spool** (`backend/models.py:66-79`)
- Represents one physical box/spool of a Product
- Links to Product via `product_id` foreign key
- Links to Order via `order_id` foreign key (optional)
- Purchase metadata: `purchase_date`, `vendor`, `price`
- Tracking: `storage_location`, `photo_path`
- Status enum: `in_stock`, `used_up`, `donated`, `lost`

**v1.1 Entities (Models added, endpoints not yet implemented):**

**Order** (`backend/models.py:112-124`)
- Represents a purchase order/invoice
- Fields: `vendor`, `order_number`, `order_date`, `invoice_path`, `total_amount`, `currency`
- Relationships: One-to-many with OrderItems, One-to-many with Spools

**OrderItem** (`backend/models.py:150-162`)
- Represents a line item from an invoice
- Fields: `order_id`, `product_id` (nullable), `title_raw`, `quantity`, `unit_price`, `status`
- Status enum: `pending_mapping` (needs product mapping) or `confirmed`
- Used for invoice parsing and product mapping workflow

**See `PHASE_5_PLAN.md` for complete Order management implementation guide.**

### API Structure

All endpoints use `/api/v1/` prefix:

**Health Check:**
- `GET /` - Returns `{"status": "ok"}`

**Products:**
- `POST /api/v1/products` - Create product
- `GET /api/v1/products` - List all products (supports ?brand, ?material, ?color_name, ?diameter_mm)
- `GET /api/v1/products/{product_id}` - Get by ID
- `PUT /api/v1/products/{product_id}` - Update product
- `DELETE /api/v1/products/{product_id}` - Delete product

**Spools:**
- `POST /api/v1/spools` - Create spool
- `GET /api/v1/spools` - List all spools (supports ?status, ?product_id, ?vendor, ?storage_location)
- `GET /api/v1/spools/{spool_id}` - Get by ID
- `PUT /api/v1/spools/{spool_id}` - Update spool
- `DELETE /api/v1/spools/{spool_id}` - Delete spool
- `POST /api/v1/spools/{spool_id}/mark-used` - Quick status update to `used_up`

**Planned but not implemented:**
- `POST /api/spools/from-photo` - OCR-based spool creation (Phase 3)
- Order management endpoints (Phase 5 - see PHASE_5_PLAN.md for specification)

### Backend Component Flow

```
Client Request → FastAPI Router (main.py)
                       ↓
                 Dependency: get_session() (database.py)
                       ↓
                 Database Session
                       ↓
                 SQLModel ORM (models.py)
                       ↓
                 SQLite Database
```

**Key architectural patterns:**
- Dependency injection for database sessions (`Depends(get_session)`)
- SQLModel provides both ORM models and Pydantic schemas
- Separate Create/Update schemas for API requests
- Test database uses in-memory SQLite with dependency override

### Frontend Architecture

**Structure:**
```
frontend/
├── src/
│   ├── App.jsx              # Main router configuration
│   ├── App.css              # Global styles (dark theme, responsive)
│   ├── components/
│   │   └── Layout.jsx       # Header, nav, footer wrapper
│   └── pages/
│       ├── InventoryPage.jsx      # Product listing with filters
│       ├── SpoolListPage.jsx      # Spool table with filters & actions
│       ├── ProductDetailPage.jsx  # Product details + spools
│       └── AddSpoolPage.jsx       # Spool creation form
├── package.json
└── vite.config.js
```

**Routing:**
- `/` or `/inventory` → InventoryPage (product grid)
- `/spools` → SpoolListPage (spool table)
- `/spools/add` → AddSpoolPage (form)
- `/products/:id` → ProductDetailPage (details)

**API Integration:**
- All pages use `fetch()` to call backend at `http://localhost:8000`
- No state management library (useState + useEffect)
- Filtering via URL query parameters

### Testing Architecture

Tests use FastAPI's TestClient with an in-memory SQLite database (`tests/test_api.py`). The test suite:
- Overrides the `get_session` dependency to use test database
- Automatically creates/drops tables between tests
- Tests full request/response cycle (integration tests)
- Validates foreign key relationships and constraints

## Project Coordination

This project follows a unique multi-agent workflow defined in README.md. Key principles:

1. **README.md is the source of truth** - The README serves as PROJECT_PLAN.md and defines all architecture, data model, and implementation phases. Consult it before making structural changes.

2. **Implementation phases** are clearly defined:
   - Phase 0: Repo initialization ✅ COMPLETE
   - Phase 1: v1 Backend (Products & Spools) ✅ **100% COMPLETE**
   - Phase 2: v1 Frontend (React UI) ✅ **COMPLETE**
   - Phase 3: v1 Label Scanning (OCR) ⏳ Not started
   - Phase 4: Deployment to Synology ⏳ Not started
   - Phase 5: v1.1 Orders & Pricing ⏳ Models added, implementation pending

3. **Stay within scope** - Don't add features beyond the current phase unless explicitly requested. The README contains detailed checklists for each phase.

4. **Next steps** (what remains to be implemented):
   - Tesseract OCR integration with pytesseract (Phase 3)
   - Brand-specific label parsers (Sunlu, eSUN, Bambu) (Phase 3)
   - Order management API endpoints (Phase 5 - models ready, see PHASE_5_PLAN.md)
   - Docker/docker-compose configuration (Phase 4)

## Development Notes

**Database location:**
- Development: `./backend/app.db` (gitignored, created automatically)
- Tests: In-memory SQLite (`:memory:`)

**API documentation:**
- FastAPI auto-generates Swagger UI at `/docs`
- ReDoc available at `/redoc`

**Code organization:**
- `backend/main.py` - FastAPI app and all route handlers
- `backend/models.py` - SQLModel definitions (Product, Spool, Order, OrderItem)
- `backend/database.py` - Database engine, session management, and init
- `backend/requirements.txt` - Python dependencies
- `tests/test_api.py` - API integration tests (8 tests)
- `frontend/src/` - React application (4 pages, 1 layout component)
- `PHASE_5_PLAN.md` - Detailed implementation plan for order management

**When adding new endpoints:**
1. Define request/response schemas in `models.py` if needed
2. Add route handler in `main.py` with proper dependency injection
3. Add tests in `tests/test_api.py`
4. Run `pytest` to verify
5. Check auto-generated docs at `/docs` to confirm schema

**SQLModel patterns used:**
- Base classes (e.g., `ProductBase`) define shared fields
- Table models (e.g., `Product`) add `id`, timestamps, and relationships
- Create schemas (e.g., `ProductCreate`) inherit from base
- Update schemas (e.g., `ProductUpdate`) make all fields Optional

**Timestamp handling:**
- All models have `created_at` and `updated_at` fields
- `created_at` auto-set on creation via `default_factory=datetime.utcnow`
- `updated_at` manually updated in PUT endpoints via `datetime.utcnow()`
