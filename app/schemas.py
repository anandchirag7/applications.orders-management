from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class ProductBase(BaseModel):
    sku: str
    name: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    status: Literal["pending", "paid", "cancelled"] = "pending"

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True
