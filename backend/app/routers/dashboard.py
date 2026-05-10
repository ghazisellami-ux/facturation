from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.models.product import Product
from app.models.invoice import Invoice, InvoiceType, InvoiceStatus
from app.models.withholding import WithholdingTax
from app.schemas.invoice import DashboardStats, InvoiceListResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de bord"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    year: Optional[int] = Query(None),
    client_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques du tableau de bord avec filtres année et client."""
    company = db.query(Company).filter(Company.owner_id == current_user.id).first()
    if not company:
        return DashboardStats(
            total_invoices=0, total_revenue=0, total_charges=0,
            paid_amount=0, total_clients=0, total_products=0,
            invoices_this_month=0, revenue_this_month=0,
            tva_a_payer=0, retenue_a_payer=0,
        )

    now = datetime.utcnow()
    current_month = now.month
    filter_year = year or now.year

    # ── Helper: base filter for invoices ──
    def inv_base(q, inv_type=InvoiceType.FACTURE.value):
        q = q.filter(
            Invoice.company_id == company.id,
            Invoice.invoice_type == inv_type,
            extract("year", Invoice.date) == filter_year,
        )
        if client_id:
            q = q.filter(Invoice.client_id == client_id)
        return q

    # Base query for factures only
    factures_query = inv_base(db.query(Invoice))

    # Total counts
    total_invoices = factures_query.count()
    total_clients = db.query(Client).filter(Client.company_id == company.id).count()
    total_products = db.query(Product).filter(Product.company_id == company.id).count()

    # Revenue
    total_revenue = inv_base(
        db.query(func.coalesce(func.sum(Invoice.total), 0))
    ).scalar()

    paid_amount = inv_base(
        db.query(func.coalesce(func.sum(Invoice.amount_paid), 0))
    ).scalar()

    # Total charges (factures d'achat)
    total_charges = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE_ACHAT.value,
        extract("year", Invoice.date) == filter_year,
    ).scalar()

    # This month
    invoices_this_month = factures_query.filter(
        extract("month", Invoice.date) == current_month,
    ).count()

    revenue_this_month_q = inv_base(
        db.query(func.coalesce(func.sum(Invoice.total), 0))
    ).filter(
        extract("month", Invoice.date) == current_month,
    )
    revenue_this_month = revenue_this_month_q.scalar()

    # ── TVA à payer = TVA vente - TVA achat ──
    tva_vente = inv_base(
        db.query(func.coalesce(func.sum(Invoice.tva_amount), 0)),
        InvoiceType.FACTURE.value
    ).scalar()

    tva_achat_q = db.query(func.coalesce(func.sum(Invoice.tva_amount), 0)).filter(
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.FACTURE_ACHAT.value,
        extract("year", Invoice.date) == filter_year,
    )
    # For purchase invoices, filter by supplier if client_id won't apply
    tva_achat = tva_achat_q.scalar()

    tva_a_payer = float(tva_vente) - float(tva_achat)

    # ── Retenue à payer = Retenue reçue - Retenue émise ──
    def wh_base(wh_type):
        q = db.query(func.coalesce(func.sum(WithholdingTax.tax_amount), 0)).filter(
            WithholdingTax.company_id == company.id,
            WithholdingTax.type == wh_type,
            extract("year", WithholdingTax.date) == filter_year,
        )
        if client_id:
            q = q.filter(WithholdingTax.client_id == client_id)
        return q

    retenue_recue = wh_base("recue").scalar()
    retenue_emise = wh_base("emise").scalar()
    retenue_a_payer = float(retenue_recue) - float(retenue_emise)

    # Recent invoices (filtered)
    recent = factures_query.order_by(Invoice.date.desc()).limit(10).all()
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

    # Monthly revenue for the selected year (Jan-Dec)
    monthly_revenue = []
    months_fr = [
        "Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
        "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"
    ]
    for m in range(1, 13):
        rev_q = db.query(func.coalesce(func.sum(Invoice.total), 0)).filter(
            Invoice.company_id == company.id,
            Invoice.invoice_type == InvoiceType.FACTURE.value,
            extract("month", Invoice.date) == m,
            extract("year", Invoice.date) == filter_year,
        )
        if client_id:
            rev_q = rev_q.filter(Invoice.client_id == client_id)

        monthly_revenue.append({
            "month": months_fr[m - 1],
            "year": filter_year,
            "revenue": float(rev_q.scalar()),
        })

    return DashboardStats(
        total_invoices=total_invoices,
        total_revenue=float(total_revenue),
        total_charges=float(total_charges),
        paid_amount=float(paid_amount),
        total_clients=total_clients,
        total_products=total_products,
        invoices_this_month=invoices_this_month,
        revenue_this_month=float(revenue_this_month),
        tva_a_payer=tva_a_payer,
        retenue_a_payer=retenue_a_payer,
        recent_invoices=recent_invoices,
        monthly_revenue=monthly_revenue,
    )
