from pydantic import BaseModel
from typing import Optional, List
import datetime


class InvoiceItemCreate(BaseModel):
    product_id: Optional[str] = None
    description: str
    quantity: float = 1.0
    unit: str = "unité"
    unit_price: float = 0.0
    discount_percent: float = 0.0
    tva_rate: float = 19.0
    fodec_rate: float = 0.0


class InvoiceItemResponse(BaseModel):
    id: str
    product_id: Optional[str] = None
    description: str
    quantity: float
    unit: str
    unit_price: float
    discount_percent: float
    tva_rate: float
    fodec_rate: float
    subtotal: float
    tva_amount: float
    fodec_amount: float
    total: float

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    client_id: Optional[str] = None
    supplier_id: Optional[str] = None
    invoice_type: str = "facture"
    date: Optional[datetime.date] = None
    due_date: Optional[datetime.date] = None
    currency: str = "TND"
    notes: Optional[str] = None
    conditions: Optional[str] = None
    timbre_fiscal: float = 1.0
    items: List[InvoiceItemCreate] = []


class InvoiceUpdate(BaseModel):
    client_id: Optional[str] = None
    status: Optional[str] = None
    date: Optional[datetime.date] = None
    due_date: Optional[datetime.date] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    conditions: Optional[str] = None
    timbre_fiscal: Optional[float] = None
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceResponse(BaseModel):
    id: str
    reference: str
    invoice_type: str
    status: str
    client_id: Optional[str] = None
    supplier_id: Optional[str] = None
    client_name: Optional[str] = None
    date: datetime.date
    due_date: Optional[datetime.date] = None
    subtotal: float
    discount_amount: float
    tva_amount: float
    fodec_amount: float
    timbre_fiscal: float
    total: float
    amount_paid: float
    balance_due: float
    currency: str
    notes: Optional[str] = None
    conditions: Optional[str] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: str
    reference: str
    invoice_type: str
    status: str
    client_name: Optional[str] = None
    date: datetime.date
    due_date: Optional[datetime.date] = None
    total: float
    amount_paid: float
    balance_due: float
    currency: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_invoices: int
    total_revenue: float
    unpaid_amount: float
    paid_amount: float
    total_clients: int
    total_products: int
    invoices_this_month: int
    revenue_this_month: float
    recent_invoices: List[InvoiceListResponse] = []
    monthly_revenue: List[dict] = []
