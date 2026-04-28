import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    reference = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    unit = Column(String, default="unité")
    unit_price = Column(Float, nullable=False, default=0.0)
    purchase_price = Column(Float, default=0.0)
    tva_rate = Column(Float, default=19.0)
    fodec_rate = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    is_service = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product")
