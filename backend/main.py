from datetime import datetime
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

app = FastAPI(title="3D Filament Scanner API", version="1.0.0")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict to frontend domain after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


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
    product.updated_at = datetime.utcnow()

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
    spool.updated_at = datetime.utcnow()

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

    Returns parsed fields: brand, material, color_name, diameter_mm, barcode, raw_text
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image bytes
    image_bytes = await file.read()

    # Parse label using OCR
    result = LabelParser.parse_label(image_bytes)

    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
