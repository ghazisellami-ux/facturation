from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SupplierCreate(BaseModel):
    name: str
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Tunisie"
    contact_name: Optional[str] = None
    notes: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_name: Optional[str] = None
    notes: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    name: str
    tax_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    contact_name: Optional[str] = None
    notes: Optional[str] = None
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True
