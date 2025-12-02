from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlmodel import Column, DateTime, Field, Relationship, SQLModel


class SpoolStatus(str, Enum):
    IN_STOCK = "in_stock"
    USED_UP = "used_up"
    DONATED = "donated"
    LOST = "lost"


class ProductBase(SQLModel):
    brand: str
    line: Optional[str] = None
    material: str
    color_name: str
    diameter_mm: float
    notes: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)),
    )

    spools: List["Spool"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    brand: Optional[str] = None
    line: Optional[str] = None
    material: Optional[str] = None
    color_name: Optional[str] = None
    diameter_mm: Optional[float] = None
    notes: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None


class SpoolBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    purchase_date: Optional[date] = None
    vendor: Optional[str] = None
    price: Optional[float] = None
    storage_location: Optional[str] = None
    photo_path: Optional[str] = None
    status: SpoolStatus = Field(default=SpoolStatus.IN_STOCK)


class Spool(SpoolBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)),
    )

    product: Optional[Product] = Relationship(back_populates="spools")


class SpoolCreate(SpoolBase):
    pass


class SpoolUpdate(SQLModel):
    product_id: Optional[int] = None
    purchase_date: Optional[date] = None
    vendor: Optional[str] = None
    price: Optional[float] = None
    storage_location: Optional[str] = None
    photo_path: Optional[str] = None
    status: Optional[SpoolStatus] = None
    order_id: Optional[int] = None
