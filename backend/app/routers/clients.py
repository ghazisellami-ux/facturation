from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/clients", tags=["Clients"])


def get_user_company(db: Session, user: User) -> Company:
    company = db.query(Company).filter(Company.owner_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Aucune entreprise trouvée")
    return company


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister tous les clients."""
    company = get_user_company(db, current_user)
    query = db.query(Client).filter(Client.company_id == company.id)

    if search:
        query = query.filter(
            Client.name.ilike(f"%{search}%") |
            Client.email.ilike(f"%{search}%") |
            Client.phone.ilike(f"%{search}%")
        )

    return query.order_by(Client.name).offset(skip).limit(limit).all()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouveau client."""
    company = get_user_company(db, current_user)
    client = Client(company_id=company.id, **data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir un client par ID."""
    company = get_user_company(db, current_user)
    client = db.query(Client).filter(
        Client.id == client_id, Client.company_id == company.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    data: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier un client."""
    company = get_user_company(db, current_user)
    client = db.query(Client).filter(
        Client.id == client_id, Client.company_id == company.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un client."""
    company = get_user_company(db, current_user)
    client = db.query(Client).filter(
        Client.id == client_id, Client.company_id == company.id
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    db.delete(client)
    db.commit()
