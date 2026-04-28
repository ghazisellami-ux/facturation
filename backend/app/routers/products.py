from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/products", tags=["Produits"])


def get_user_company(db: Session, user: User) -> Company:
    company = db.query(Company).filter(Company.owner_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Aucune entreprise trouvée")
    return company


@router.get("/", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister tous les produits."""
    company = get_user_company(db, current_user)
    query = db.query(Product).filter(Product.company_id == company.id)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%") |
            Product.reference.ilike(f"%{search}%")
        )
    if category:
        query = query.filter(Product.category == category)

    return query.order_by(Product.name).offset(skip).limit(limit).all()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouveau produit."""
    company = get_user_company(db, current_user)
    product = Product(company_id=company.id, **data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir un produit par ID."""
    company = get_user_company(db, current_user)
    product = db.query(Product).filter(
        Product.id == product_id, Product.company_id == company.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier un produit."""
    company = get_user_company(db, current_user)
    product = db.query(Product).filter(
        Product.id == product_id, Product.company_id == company.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un produit."""
    company = get_user_company(db, current_user)
    product = db.query(Product).filter(
        Product.id == product_id, Product.company_id == company.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    db.delete(product)
    db.commit()
