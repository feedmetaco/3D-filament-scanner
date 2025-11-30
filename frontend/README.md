# 3D Filament Scanner - Frontend

React frontend for the 3D Filament Scanner inventory management application.

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Vanilla CSS** - Styling (mobile-friendly)

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Pages

- **/ (InventoryPage)** - View all products with filtering by brand, material, color
- **/spools** - View all spools with filtering by status, vendor, location
- **/spools/add** - Add a new spool
- **/products/:id** - View product details and associated spools

## API Integration

The frontend expects the backend API to be running at `http://localhost:8000`. All API calls use:

- `GET /api/v1/products` - List products with optional filters
- `GET /api/v1/products/:id` - Get product details
- `GET /api/v1/spools` - List spools with optional filters
- `POST /api/v1/spools` - Create new spool
- `POST /api/v1/spools/:id/mark-used` - Mark spool as used

## Features Implemented

✅ Product inventory view with filtering
✅ Spool list view with filtering
✅ Product detail page showing associated spools
✅ Add spool form with product selection
✅ Quick "Mark Used" button for spools
✅ Mobile-responsive design
✅ Clean, modern UI with dark theme

## Not Yet Implemented

⏳ Photo upload for label scanning (Phase 3)
⏳ OCR integration (Phase 3)
⏳ Order management (Phase 5)

## Notes

- Currently hardcoded to use `http://localhost:8000` for API calls
- For production, configure environment variables or update API base URL
- Uses browser's fetch API (no axios or other HTTP library)
