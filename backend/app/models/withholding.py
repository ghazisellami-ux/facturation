import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, DateTime, Date, ForeignKey, Text, Enum
from app.database import Base
import enum


class WithholdingType(str, enum.Enum):
    EMISE = "emise"      # Retenue émise (on retient sur nos paiements)
    RECUE = "recue"      # Retenue reçue (nos clients retiennent sur nous)


class WithholdingTax(Base):
    __tablename__ = "withholding_taxes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    type = Column(String, nullable=False, default="emise")  # emise / recue
    rate = Column(Float, nullable=False, default=1.0)  # 1% ou 3%
    base_amount = Column(Float, nullable=False, default=0.0)  # Montant de base HT
    tax_amount = Column(Float, nullable=False, default=0.0)  # Montant retenu
    date = Column(Date, nullable=False, default=date.today)
    reference = Column(String, nullable=True)  # Référence du certificat
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=True)  # Facture liée
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)  # Client concerné
    supplier_id = Column(String, ForeignKey("suppliers.id"), nullable=True)  # Fournisseur concerné
    beneficiary_name = Column(String, nullable=True)  # Nom du bénéficiaire (si pas client/fournisseur)
    beneficiary_tax_id = Column(String, nullable=True)  # MF du bénéficiaire
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
