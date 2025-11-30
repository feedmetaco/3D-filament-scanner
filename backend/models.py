from datetime import date, datetime
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
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    spools: List["Spool"] = Relationship(back_populates="product")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


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
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    product: Optional[Product] = Relationship(back_populates="spools")
    order: Optional["Order"] = Relationship(back_populates="spools")


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


# Phase 5 (v1.1): Order Management Models


class OrderItemStatus(str, Enum):
    PENDING_MAPPING = "pending_mapping"
    CONFIRMED = "confirmed"


class OrderBase(SQLModel):
    vendor: str
    order_number: str
    order_date: Optional[date] = None
    invoice_path: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "USD"


class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    items: List["OrderItem"] = Relationship(back_populates="order")
    spools: List["Spool"] = Relationship(back_populates="order")


class OrderCreate(OrderBase):
    pass


class OrderUpdate(SQLModel):
    vendor: Optional[str] = None
    order_number: Optional[str] = None
    order_date: Optional[date] = None
    invoice_path: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None


class OrderItemBase(SQLModel):
    order_id: int = Field(foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    title_raw: str
    quantity: int
    unit_price: float
    currency: str = "USD"
    status: OrderItemStatus = Field(default=OrderItemStatus.PENDING_MAPPING)


class OrderItem(OrderItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(SQLModel):
    product_id: Optional[int] = None
    title_raw: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[OrderItemStatus] = None
