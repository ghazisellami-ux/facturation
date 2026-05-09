"""
Router pour la gestion des retenues à la source.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.withholding import WithholdingTax
from app.models.client import Client
from app.models.supplier import Supplier
from app.utils.auth import get_current_user
from app.routers.invoices import get_user_company

router = APIRouter(prefix="/api/withholdings", tags=["Withholdings"])


class WithholdingCreate(BaseModel):
    type: str  # emise / recue
    rate: float  # 1.0 ou 3.0
    base_amount: float
    date: str
    reference: Optional[str] = None
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    supplier_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_tax_id: Optional[str] = None
    notes: Optional[str] = None


class WithholdingUpdate(BaseModel):
    type: Optional[str] = None
    rate: Optional[float] = None
    base_amount: Optional[float] = None
    date: Optional[str] = None
    reference: Optional[str] = None
    invoice_id: Optional[str] = None
    client_id: Optional[str] = None
    supplier_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_tax_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
def list_withholdings(
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company = get_user_company(db, current_user)
    q = db.query(WithholdingTax).filter(WithholdingTax.company_id == company.id)
    if type:
        q = q.filter(WithholdingTax.type == type)
    if search:
        q = q.filter(
            (WithholdingTax.reference.ilike(f"%{search}%")) |
            (WithholdingTax.beneficiary_name.ilike(f"%{search}%")) |
            (WithholdingTax.notes.ilike(f"%{search}%"))
        )
    items = q.order_by(WithholdingTax.date.desc()).offset(skip).limit(limit).all()

    results = []
    for w in items:
        # Resolve names
        name = w.beneficiary_name or ""
        tax_id = w.beneficiary_tax_id or ""
        if w.client_id:
            client = db.query(Client).filter(Client.id == w.client_id).first()
            if client:
                name = client.name
                tax_id = client.tax_id or ""
        elif w.supplier_id:
            supplier = db.query(Supplier).filter(Supplier.id == w.supplier_id).first()
            if supplier:
                name = supplier.name
                tax_id = supplier.tax_id or ""

        results.append({
            "id": w.id,
            "type": w.type,
            "rate": w.rate,
            "base_amount": w.base_amount,
            "tax_amount": w.tax_amount,
            "date": w.date.isoformat() if w.date else None,
            "reference": w.reference,
            "invoice_id": w.invoice_id,
            "client_id": w.client_id,
            "supplier_id": w.supplier_id,
            "beneficiary_name": name,
            "beneficiary_tax_id": tax_id,
            "notes": w.notes,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        })

    return {"data": results, "total": q.count()}


@router.post("/")
def create_withholding(
    data: WithholdingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company = get_user_company(db, current_user)

    if data.rate not in (1.0, 3.0, 1, 3):
        raise HTTPException(status_code=400, detail="Le taux doit être 1% ou 3%")
    if data.type not in ("emise", "recue"):
        raise HTTPException(status_code=400, detail="Le type doit être 'emise' ou 'recue'")

    tax_amount = data.base_amount * data.rate / 100

    w = WithholdingTax(
        company_id=company.id,
        type=data.type,
        rate=data.rate,
        base_amount=data.base_amount,
        tax_amount=tax_amount,
        date=data.date,
        reference=data.reference,
        invoice_id=data.invoice_id or None,
        client_id=data.client_id or None,
        supplier_id=data.supplier_id or None,
        beneficiary_name=data.beneficiary_name,
        beneficiary_tax_id=data.beneficiary_tax_id,
        notes=data.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(w)
    db.commit()
    db.refresh(w)

    return {"id": w.id, "tax_amount": w.tax_amount, "message": "Retenue créée"}


@router.put("/{withholding_id}")
def update_withholding(
    withholding_id: str,
    data: WithholdingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company = get_user_company(db, current_user)
    w = db.query(WithholdingTax).filter(
        WithholdingTax.id == withholding_id, WithholdingTax.company_id == company.id
    ).first()
    if not w:
        raise HTTPException(status_code=404, detail="Retenue non trouvée")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("client_id", "supplier_id", "invoice_id") and value == "":
            value = None
        setattr(w, key, value)

    # Recalculate tax_amount
    w.tax_amount = w.base_amount * w.rate / 100
    w.updated_at = datetime.utcnow()

    db.commit()
    return {"message": "Retenue mise à jour"}


@router.delete("/{withholding_id}")
def delete_withholding(
    withholding_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    company = get_user_company(db, current_user)
    w = db.query(WithholdingTax).filter(
        WithholdingTax.id == withholding_id, WithholdingTax.company_id == company.id
    ).first()
    if not w:
        raise HTTPException(status_code=404, detail="Retenue non trouvée")
    db.delete(w)
    db.commit()
    return {"message": "Retenue supprimée"}
