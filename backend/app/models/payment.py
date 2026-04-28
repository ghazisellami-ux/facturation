import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    ESPECES = "especes"
    CHEQUE = "cheque"
    VIREMENT = "virement"
    CARTE = "carte"
    TRAITE = "traite"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(String, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, default=date.today)
    method = Column(String, default=PaymentMethod.ESPECES.value)
    reference = Column(String, nullable=True)  # Numéro chèque, etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
