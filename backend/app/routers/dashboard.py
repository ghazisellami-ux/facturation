from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.models.product import Product
from app.models.invoice import Invoice, InvoiceType, InvoiceStatus
from app.schemas.invoice import DashboardStats, InvoiceListResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de bord"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques du tableau de bord."""
    company = db.query(Company).filter(Company.owner_id == current_user.id).first()
    if not company:
        return DashboardStats(
            total_invoices=0, total_revenue=0, unpaid_amount=0,
            paid_amount=0, total_clients=0, total_products=0,
            invoices_this_month=0, revenue_this_month=0,
        )

    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year

    # Base query for factures only
    factures_query = db.query(Invoice).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE.value
    )

    # Total counts
    total_invoices = factures_query.count()
    total_clients = db.query(Client).filter(Client.company_id == company.id).count()
    total_products = db.query(Product).filter(Product.company_id == company.id).count()

    # Revenue
    total_revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE.value
    ).scalar()

    paid_amount = db.query(func.coalesce(func.sum(Invoice.amount_paid), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE.value
    ).scalar()

    unpaid_amount = db.query(func.coalesce(func.sum(Invoice.balance_due), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE.value,
        Invoice.status.in_([
            InvoiceStatus.ENVOYEE.value,
            InvoiceStatus.PARTIELLEMENT_PAYEE.value,
            InvoiceStatus.EN_RETARD.value,
            InvoiceStatus.BROUILLON.value,
        ])
    ).scalar()

    # This month
    invoices_this_month = factures_query.filter(
        extract("month", Invoice.date) == current_month,
        extract("year", Invoice.date) == current_year,
    ).count()

    revenue_this_month = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE.value,
        extract("month", Invoice.date) == current_month,
        extract("year", Invoice.date) == current_year,
    ).scalar()

    # Recent invoices
    recent = factures_query.order_by(Invoice.created_at.desc()).limit(5).all()
    recent_invoices = []
    for inv in recent:
        client = db.query(Client).filter(Client.id == inv.client_id).first() if inv.client_id else None
        recent_invoices.append(InvoiceListResponse(
            id=inv.id,
            reference=inv.reference,
            invoice_type=inv.invoice_type,
            status=inv.status,
            client_name=client.name if client else None,
            date=inv.date,
            due_date=inv.due_date,
            total=inv.total,
            amount_paid=inv.amount_paid,
            balance_due=inv.balance_due,
            currency=inv.currency,
            created_at=inv.created_at,
        ))

    # Monthly revenue (last 12 months)
    monthly_revenue = []
    for i in range(11, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1

        rev = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
            Invoice.company_id == company.id,
            Invoice.invoice_type == InvoiceType.FACTURE.value,
            extract("month", Invoice.date) == month,
            extract("year", Invoice.date) == year,
        ).scalar()

        months_fr = [
            "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
            "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"
        ]
        monthly_revenue.append({
            "month": months_fr[month - 1],
            "year": year,
            "revenue": float(rev),
        })

    return DashboardStats(
        total_invoices=total_invoices,
        total_revenue=float(total_revenue),
        unpaid_amount=float(unpaid_amount),
        paid_amount=float(paid_amount),
        total_clients=total_clients,
        total_products=total_products,
        invoices_this_month=invoices_this_month,
        revenue_this_month=float(revenue_this_month),
        recent_invoices=recent_invoices,
        monthly_revenue=monthly_revenue,
    )
