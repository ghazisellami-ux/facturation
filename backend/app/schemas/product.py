from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    reference: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "unité"
    unit_price: float = 0.0
    purchase_price: float = 0.0
    tva_rate: float = 19.0
    fodec_rate: float = 0.0
    stock_quantity: int = 0
    min_stock: int = 0
    is_service: bool = False


class ProductUpdate(BaseModel):
    reference: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    purchase_price: Optional[float] = None
    tva_rate: Optional[float] = None
    fodec_rate: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock: Optional[int] = None
    is_service: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    reference: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str
    unit_price: float
    purchase_price: float
    tva_rate: float
    fodec_rate: float
    stock_quantity: int
    min_stock: int
    is_service: bool
    created_at: datetime

    class Config:
        from_attributes = True
