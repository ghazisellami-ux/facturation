from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Tunisie"
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    currency: str = "TND"
    default_tva_rate: float = 19.0


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    currency: Optional[str] = None
    default_tva_rate: Optional[float] = None
    invoice_prefix: Optional[str] = None
    devis_prefix: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    tax_id: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    currency: str
    default_tva_rate: float
    invoice_prefix: str
    devis_prefix: str
    created_at: datetime

    class Config:
        from_attributes = True
