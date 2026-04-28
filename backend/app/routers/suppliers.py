from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/suppliers", tags=["Fournisseurs"])


def get_user_company(db: Session, user: User) -> Company:
    company = db.query(Company).filter(Company.owner_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Aucune entreprise trouvée")
    return company


@router.get("/", response_model=List[SupplierResponse])
def list_suppliers(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister tous les fournisseurs."""
    company = get_user_company(db, current_user)
    query = db.query(Supplier).filter(Supplier.company_id == company.id)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%"))
    return query.order_by(Supplier.name).all()


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    data: SupplierCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouveau fournisseur."""
    company = get_user_company(db, current_user)
    supplier = Supplier(company_id=company.id, **data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier un fournisseur."""
    company = get_user_company(db, current_user)
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id, Supplier.company_id == company.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")

    update_fields = data.model_dump(exclude_unset=True)
    for key, value in update_fields.items():
        setattr(supplier, key, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(
    supplier_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un fournisseur."""
    company = get_user_company(db, current_user)
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id, Supplier.company_id == company.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    db.delete(supplier)
    db.commit()
