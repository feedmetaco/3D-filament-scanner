from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

from backend.database import get_session, init_db
from backend.models import (
    Product,
    ProductCreate,
    ProductUpdate,
    Spool,
    SpoolCreate,
    SpoolStatus,
    SpoolUpdate,
)

app = FastAPI(title="3D Filament Scanner API", version="1.0.0")


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
    brand: str | None = None,
    material: str | None = None,
    color_name: str | None = None,
    diameter_mm: float | None = None,
    session: Session = Depends(get_session),
) -> List[Product]:
    query = select(Product)
    if brand:
        query = query.where(Product.brand == brand)
    if material:
        query = query.where(Product.material == material)
    if color_name:
        query = query.where(Product.color_name == color_name)
    if diameter_mm:
        query = query.where(Product.diameter_mm == diameter_mm)
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
    status: str | None = None,
    product_id: int | None = None,
    vendor: str | None = None,
    storage_location: str | None = None,
    session: Session = Depends(get_session),
) -> List[Spool]:
    query = select(Spool)
    if status:
        query = query.where(Spool.status == status)
    if product_id:
        query = query.where(Spool.product_id == product_id)
    if vendor:
        query = query.where(Spool.vendor == vendor)
    if storage_location:
        query = query.where(Spool.storage_location == storage_location)
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


@app.post("/api/v1/spools/{spool_id}/mark-used", response_model=Spool, tags=["spools"])
def mark_spool_used(spool_id: int, session: Session = Depends(get_session)) -> Spool:
    spool = session.get(Spool, spool_id)
    if not spool:
        raise HTTPException(status_code=404, detail="Spool not found")

    spool.status = SpoolStatus.USED_UP
    spool.updated_at = datetime.utcnow()

    session.add(spool)
    session.commit()
    session.refresh(spool)
    return spool


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
