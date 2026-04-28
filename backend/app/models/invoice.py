import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Date, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class InvoiceType(str, enum.Enum):
    FACTURE = "facture"
    DEVIS = "devis"
    BON_LIVRAISON = "bon_livraison"
    BON_COMMANDE = "bon_commande"
    AVOIR = "avoir"


class InvoiceStatus(str, enum.Enum):
    BROUILLON = "brouillon"
    ENVOYEE = "envoyee"
    PAYEE = "payee"
    PARTIELLEMENT_PAYEE = "partiellement_payee"
    EN_RETARD = "en_retard"
    ANNULEE = "annulee"
    # Devis specific
    ACCEPTE = "accepte"
    REFUSE = "refuse"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    reference = Column(String, nullable=False, index=True)
    invoice_type = Column(String, default=InvoiceType.FACTURE.value)
    status = Column(String, default=InvoiceStatus.BROUILLON.value)
    date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=True)

    # Amounts
    subtotal = Column(Float, default=0.0)  # Total HT
    discount_amount = Column(Float, default=0.0)
    tva_amount = Column(Float, default=0.0)
    fodec_amount = Column(Float, default=0.0)
    timbre_fiscal = Column(Float, default=1.0)
    total = Column(Float, default=0.0)  # Net à payer (TTC)
    amount_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)

    # Details
    currency = Column(String, default="TND")
    notes = Column(Text, nullable=True)
    conditions = Column(Text, nullable=True)
    footer_note = Column(Text, nullable=True)

    # Source (for converted documents)
    source_invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    source_invoice = relationship("Invoice", remote_side=[id], foreign_keys=[source_invoice_id])


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(String, ForeignKey("products.id"), nullable=True)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="unité")
    unit_price = Column(Float, default=0.0)
    discount_percent = Column(Float, default=0.0)
    tva_rate = Column(Float, default=19.0)
    fodec_rate = Column(Float, default=0.0)

    # Calculated
    subtotal = Column(Float, default=0.0)  # qty * price - discount
    tva_amount = Column(Float, default=0.0)
    fodec_amount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)

    sort_order = Column(Integer, default=0)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")
