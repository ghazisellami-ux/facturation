"""
Gestion des utilisateurs (admin).
Permet de créer, lister, modifier et supprimer des utilisateurs.
Chaque utilisateur créé reçoit automatiquement sa propre entreprise.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.models.invoice import Invoice
from app.utils.auth import get_current_user, hash_password
from pydantic import BaseModel, EmailStr
from datetime import datetime


router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


# ── Schemas ──

class UserCreateAdmin(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None


class UserUpdateAdmin(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    company_name: Optional[str] = None


class UserListResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool
    company_name: Optional[str] = None
    total_invoices: int = 0
    total_clients: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ── Endpoints ──

@router.get("/", response_model=list[UserListResponse])
def list_users(
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister tous les utilisateurs."""
    q = db.query(User)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            (User.first_name.ilike(pattern)) |
            (User.last_name.ilike(pattern)) |
            (User.email.ilike(pattern))
        )
    q = q.order_by(User.created_at.desc())
    users = q.all()

    result = []
    for u in users:
        company = db.query(Company).filter(Company.owner_id == u.id).first()
        total_invoices = 0
        total_clients = 0
        if company:
            total_invoices = db.query(func.count(Invoice.id)).filter(Invoice.company_id == company.id).scalar() or 0
            total_clients = db.query(func.count(Client.id)).filter(Client.company_id == company.id).scalar() or 0

        result.append(UserListResponse(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            phone=u.phone,
            is_active=u.is_active,
            company_name=company.name if company else None,
            total_invoices=total_invoices,
            total_clients=total_clients,
            created_at=u.created_at,
        ))
    return result


@router.post("/", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreateAdmin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Créer un nouvel utilisateur avec sa propre entreprise."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
    )
    db.add(user)
    db.flush()

    company_name = data.company_name or f"Entreprise de {data.first_name}"
    company = Company(
        name=company_name,
        owner_id=user.id,
        email=data.email,
        phone=data.phone,
    )
    db.add(company)
    db.commit()
    db.refresh(user)

    return UserListResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_active=user.is_active,
        company_name=company.name,
        total_invoices=0,
        total_clients=0,
        created_at=user.created_at,
    )


@router.put("/{user_id}", response_model=UserListResponse)
def update_user(
    user_id: str,
    data: UserUpdateAdmin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Modifier un utilisateur."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    update_fields = data.model_dump(exclude_unset=True)

    # Handle company_name separately
    company_name_update = update_fields.pop("company_name", None)
    if company_name_update is not None:
        company = db.query(Company).filter(Company.owner_id == user.id).first()
        if company:
            company.name = company_name_update

    # Check email uniqueness
    if "email" in update_fields and update_fields["email"] != user.email:
        existing = db.query(User).filter(User.email == update_fields["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    for key, value in update_fields.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    company = db.query(Company).filter(Company.owner_id == user.id).first()
    total_invoices = 0
    total_clients = 0
    if company:
        total_invoices = db.query(func.count(Invoice.id)).filter(Invoice.company_id == company.id).scalar() or 0
        total_clients = db.query(func.count(Client.id)).filter(Client.company_id == company.id).scalar() or 0

    return UserListResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_active=user.is_active,
        company_name=company.name if company else None,
        total_invoices=total_invoices,
        total_clients=total_clients,
        created_at=user.created_at,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprimer un utilisateur et toutes ses données."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(user)
    db.commit()


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Réinitialiser le mot de passe d'un utilisateur."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    new_password = data.get("password")
    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 4 caractères")

    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Mot de passe réinitialisé avec succès"}
