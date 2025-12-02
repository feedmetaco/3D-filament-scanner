from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from backend.database import get_session, init_db
from backend.models import (
    Product,
    ProductCreate,
    ProductUpdate,
    Spool,
    SpoolCreate,
    SpoolUpdate,
)
from backend.ocr_service import LabelParser
from backend.invoice_parser import InvoiceParser


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed in future)


app = FastAPI(
    title="3D Filament Scanner API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict to frontend domain after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def read_root() -> dict[str, str]:
    return {"status": "ok"}


# Product Endpoints
@app.post("/api/v1/products", response_model=Product, tags=["products"])
def create_product(
    product_in: ProductCreate, session: Session = Depends(get_session)
) -> Product:
    product = Product(**product_in.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.get("/api/v1/products", response_model=List[Product], tags=["products"])
def list_products(
    brand: Optional[str] = None,
    material: Optional[str] = None,
    color_name: Optional[str] = None,
    session: Session = Depends(get_session)
) -> List[Product]:
    """List products with optional filtering by brand, material, and color_name."""
    query = select(Product)

    if brand:
        query = query.where(Product.brand.ilike(f"%{brand}%"))
    if material:
        query = query.where(Product.material.ilike(f"%{material}%"))
    if color_name:
        query = query.where(Product.color_name.ilike(f"%{color_name}%"))

    products = session.exec(query).all()
    return products


@app.get("/api/v1/products/{product_id}", response_model=Product, tags=["products"])
def get_product(product_id: int, session: Session = Depends(get_session)) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/v1/products/{product_id}", response_model=Product, tags=["products"])
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    session: Session = Depends(get_session),
) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    product.updated_at = datetime.now(timezone.utc)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.delete("/api/v1/products/{product_id}", status_code=204, tags=["products"])
def delete_product(product_id: int, session: Session = Depends(get_session)) -> None:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(product)
    session.commit()


# Spool Endpoints
@app.post("/api/v1/spools", response_model=Spool, tags=["spools"])
def create_spool(spool_in: SpoolCreate, session: Session = Depends(get_session)) -> Spool:
    spool = Spool(**spool_in.model_dump())
    session.add(spool)
    session.commit()
    session.refresh(spool)
    return spool


@app.get("/api/v1/spools", response_model=List[Spool], tags=["spools"])
def list_spools(
    status: Optional[str] = None,
    session: Session = Depends(get_session)
) -> List[Spool]:
    """List spools with optional filtering by status."""
    query = select(Spool)

    if status:
        query = query.where(Spool.status == status)

    spools = session.exec(query).all()
    return spools


@app.get("/api/v1/spools/{spool_id}", response_model=Spool, tags=["spools"])
def get_spool(spool_id: int, session: Session = Depends(get_session)) -> Spool:
    spool = session.get(Spool, spool_id)
    if not spool:
        raise HTTPException(status_code=404, detail="Spool not found")
    return spool


@app.put("/api/v1/spools/{spool_id}", response_model=Spool, tags=["spools"])
def update_spool(
    spool_id: int, spool_in: SpoolUpdate, session: Session = Depends(get_session)
) -> Spool:
    spool = session.get(Spool, spool_id)
    if not spool:
        raise HTTPException(status_code=404, detail="Spool not found")

    update_data = spool_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(spool, key, value)
    spool.updated_at = datetime.now(timezone.utc)

    session.add(spool)
    session.commit()
    session.refresh(spool)
    return spool


@app.delete("/api/v1/spools/{spool_id}", status_code=204, tags=["spools"])
def delete_spool(spool_id: int, session: Session = Depends(get_session)) -> None:
    spool = session.get(Spool, spool_id)
    if not spool:
        raise HTTPException(status_code=404, detail="Spool not found")
    session.delete(spool)
    session.commit()


# OCR Endpoint
@app.post("/api/v1/ocr/parse-label", tags=["ocr"])
async def parse_label(file: UploadFile = File(...)):
    """
    Upload a filament box label image and extract structured data.

    Returns parsed fields: brand, material, color_name, diameter_mm, barcode, raw_text, ocr_confidence, strategy_used

    The raw_text field shows exactly what Tesseract OCR extracted from the image.
    This is useful for debugging when fields are not detected correctly.
    
    The ocr_confidence field indicates OCR quality (0-100).
    The strategy_used field shows which preprocessing strategy worked best.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Parse label using OCR
        from backend.ocr_service import OCRError
        try:
            result = LabelParser.parse_label(image_bytes)
            return result
        except OCRError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )


# Invoice Parsing Endpoint
@app.post("/api/v1/invoice/parse", tags=["invoice"])
async def parse_invoice(file: UploadFile = File(...)):
    """
    Upload a PDF invoice and extract order information with all filament products.

    Returns:
    - order_number: Order ID from invoice
    - order_date: Purchase date
    - vendor: Vendor name (e.g., "Bambu Lab", "Amazon")
    - items: List of products with brand, material, color_name, diameter_mm, quantity, price
    """
    # Validate file type
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Read PDF bytes
    pdf_bytes = await file.read()

    try:
        # Parse invoice
        result = InvoiceParser.parse_invoice(pdf_bytes)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse invoice: {str(e)}")


# Bulk Import from Invoice
@app.post("/api/v1/invoice/import", tags=["invoice"])
async def import_from_invoice(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload a PDF invoice and automatically create Products and Spools for all items.

    This endpoint:
    1. Parses the invoice to extract all filament products
    2. Creates or finds matching Product records
    3. Creates Spool records for each quantity with purchase details
    4. Returns summary of created records

    Returns:
    - products_created: Number of new products
    - spools_created: Number of new spools
    - order_number: Order ID from invoice
    - items: List of created products and spools
    """
    # Validate file type
    if not file.content_type or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Read PDF bytes
    pdf_bytes = await file.read()

    try:
        # Parse invoice
        invoice_data = InvoiceParser.parse_invoice(pdf_bytes)

        products_created = 0
        spools_created = 0
        imported_items = []

        for item in invoice_data["items"]:
            # Check if product exists
            query = select(Product).where(
                Product.brand == item["brand"],
                Product.material == item["material"],
                Product.color_name == item["color_name"],
                Product.diameter_mm == item["diameter_mm"]
            )
            existing_product = session.exec(query).first()

            if existing_product:
                product = existing_product
            else:
                # Create new product
                product = Product(
                    brand=item["brand"],
                    material=item["material"],
                    color_name=item["color_name"],
                    diameter_mm=item["diameter_mm"],
                    line=item.get("product_line"),
                    sku=item.get("sku")
                )
                session.add(product)
                session.flush()  # Get product ID
                products_created += 1

            # Create spools for each quantity
            for _ in range(item["quantity"]):
                spool = Spool(
                    product_id=product.id,
                    purchase_date=invoice_data["order_date"],
                    vendor=invoice_data["vendor"],
                    price=item.get("price"),
                    status="in_stock"
                )
                session.add(spool)
                spools_created += 1

            imported_items.append({
                "product_id": product.id,
                "brand": product.brand,
                "material": product.material,
                "color_name": product.color_name,
                "quantity": item["quantity"],
                "price": item.get("price")
            })

        session.commit()

        return {
            "success": True,
            "products_created": products_created,
            "spools_created": spools_created,
            "order_number": invoice_data["order_number"],
            "order_date": invoice_data["order_date"],
            "vendor": invoice_data["vendor"],
            "items": imported_items
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import invoice: {str(e)}")


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
