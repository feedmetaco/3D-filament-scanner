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
def list_products(session: Session = Depends(get_session)) -> List[Product]:
    products = session.exec(select(Product)).all()
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
def list_spools(session: Session = Depends(get_session)) -> List[Spool]:
    spools = session.exec(select(Spool)).all()
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
