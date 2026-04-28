from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.client import Client
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.invoice import Invoice, InvoiceItem, InvoiceType, InvoiceStatus
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    InvoiceListResponse, InvoiceItemCreate, DashboardStats
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/invoices", tags=["Factures"])


def get_user_company(db: Session, user: User) -> Company:
    company = db.query(Company).filter(Company.owner_id == user.id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Aucune entreprise trouvée")
    return company


def calculate_item_totals(item_data: InvoiceItemCreate) -> dict:
    """Calculate line item totals with Tunisian tax."""
    subtotal = item_data.quantity * item_data.unit_price
    discount = subtotal * (item_data.discount_percent / 100)
    subtotal_after_discount = subtotal - discount
    fodec_amount = subtotal_after_discount * (item_data.fodec_rate / 100)
    taxable_amount = subtotal_after_discount + fodec_amount
    tva_amount = taxable_amount * (item_data.tva_rate / 100)
    total = taxable_amount + tva_amount

    return {
        "subtotal": round(subtotal_after_discount, 3),
        "fodec_amount": round(fodec_amount, 3),
        "tva_amount": round(tva_amount, 3),
        "total": round(total, 3),
    }


def generate_reference(db: Session, company: Company, invoice_type: str) -> str:
    """Generate next invoice reference number."""
    year = datetime.now().year
    if invoice_type == InvoiceType.DEVIS.value:
        prefix = company.devis_prefix
        next_num = int(company.devis_next_number)
        company.devis_next_number = str(next_num + 1)
    elif invoice_type == InvoiceType.FACTURE_ACHAT.value:
        prefix = "ACH"
        # Count existing purchase invoices this year for numbering
        count = db.query(Invoice).filter(
            Invoice.company_id == company.id,
            Invoice.invoice_type == InvoiceType.FACTURE_ACHAT.value,
        ).count()
        next_num = count + 1
    else:
        prefix = company.invoice_prefix
        next_num = int(company.invoice_next_number)
        company.invoice_next_number = str(next_num + 1)

    return f"{prefix}-{year}{str(next_num).zfill(4)}"


@router.get("/", response_model=List[InvoiceListResponse])
def list_invoices(
    invoice_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister toutes les factures/devis."""
    company = get_user_company(db, current_user)
    query = db.query(Invoice).filter(Invoice.company_id == company.id)

    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    if search:
        query = query.filter(Invoice.reference.ilike(f"%{search}%"))

    invoices = query.order_by(Invoice.date.desc()).offset(skip).limit(limit).all()

    result = []
    for inv in invoices:
        client = db.query(Client).filter(Client.id == inv.client_id).first() if inv.client_id else None
        supplier = db.query(Supplier).filter(Supplier.id == inv.supplier_id).first() if inv.supplier_id else None
        display_name = client.name if client else (supplier.name if supplier else None)
        result.append(InvoiceListResponse(
            id=inv.id,
            reference=inv.reference,
            invoice_type=inv.invoice_type,
            status=inv.status,
            client_name=display_name,
            date=inv.date,
            due_date=inv.due_date,
            total=inv.total,
            amount_paid=inv.amount_paid,
            balance_due=inv.balance_due,
            currency=inv.currency,
            created_at=inv.created_at,
        ))
    return result


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    data: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer une nouvelle facture/devis."""
    company = get_user_company(db, current_user)

    # Generate reference
    reference = generate_reference(db, company, data.invoice_type)

    # Create invoice
    invoice = Invoice(
        company_id=company.id,
        client_id=data.client_id,
        supplier_id=data.supplier_id,
        reference=reference,
        invoice_type=data.invoice_type,
        date=data.date or date.today(),
        due_date=data.due_date,
        currency=data.currency,
        notes=data.notes,
        conditions=data.conditions,
        timbre_fiscal=data.timbre_fiscal,
    )
    db.add(invoice)
    db.flush()

    # Create items and calculate totals
    total_subtotal = 0
    total_tva = 0
    total_fodec = 0
    total_discount = 0

    for i, item_data in enumerate(data.items):
        totals = calculate_item_totals(item_data)
        item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.product_id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            discount_percent=item_data.discount_percent,
            tva_rate=item_data.tva_rate,
            fodec_rate=item_data.fodec_rate,
            subtotal=totals["subtotal"],
            tva_amount=totals["tva_amount"],
            fodec_amount=totals["fodec_amount"],
            total=totals["total"],
            sort_order=i,
        )
        db.add(item)
        total_subtotal += totals["subtotal"]
        total_tva += totals["tva_amount"]
        total_fodec += totals["fodec_amount"]
        discount = item_data.quantity * item_data.unit_price * (item_data.discount_percent / 100)
        total_discount += discount

    # Update invoice totals
    invoice.subtotal = round(total_subtotal, 3)
    invoice.discount_amount = round(total_discount, 3)
    invoice.tva_amount = round(total_tva, 3)
    invoice.fodec_amount = round(total_fodec, 3)
    invoice.total = round(total_subtotal + total_tva + total_fodec + invoice.timbre_fiscal, 3)
    invoice.balance_due = invoice.total

    db.commit()
    db.refresh(invoice)

    # Build response
    client = db.query(Client).filter(Client.id == invoice.client_id).first() if invoice.client_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.sort_order).all()

    return InvoiceResponse(
        id=invoice.id,
        reference=invoice.reference,
        invoice_type=invoice.invoice_type,
        status=invoice.status,
        client_id=invoice.client_id,
        supplier_id=invoice.supplier_id,
        client_name=client.name if client else None,
        date=invoice.date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        discount_amount=invoice.discount_amount,
        tva_amount=invoice.tva_amount,
        fodec_amount=invoice.fodec_amount,
        timbre_fiscal=invoice.timbre_fiscal,
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        balance_due=invoice.balance_due,
        currency=invoice.currency,
        notes=invoice.notes,
        conditions=invoice.conditions,
        items=items,
        created_at=invoice.created_at,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtenir une facture par ID."""
    company = get_user_company(db, current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.company_id == company.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    client = db.query(Client).filter(Client.id == invoice.client_id).first() if invoice.client_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.sort_order).all()

    return InvoiceResponse(
        id=invoice.id,
        reference=invoice.reference,
        invoice_type=invoice.invoice_type,
        status=invoice.status,
        client_id=invoice.client_id,
        client_name=client.name if client else None,
        date=invoice.date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        discount_amount=invoice.discount_amount,
        tva_amount=invoice.tva_amount,
        fodec_amount=invoice.fodec_amount,
        timbre_fiscal=invoice.timbre_fiscal,
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        balance_due=invoice.balance_due,
        currency=invoice.currency,
        notes=invoice.notes,
        conditions=invoice.conditions,
        items=items,
        created_at=invoice.created_at,
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modifier une facture."""
    company = get_user_company(db, current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.company_id == company.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    # Update basic fields
    update_fields = data.model_dump(exclude_unset=True, exclude={"items"})
    for key, value in update_fields.items():
        setattr(invoice, key, value)

    # Update items if provided
    if data.items is not None:
        # Delete existing items
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).delete()

        total_subtotal = 0
        total_tva = 0
        total_fodec = 0
        total_discount = 0

        for i, item_data in enumerate(data.items):
            totals = calculate_item_totals(item_data)
            item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item_data.product_id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit=item_data.unit,
                unit_price=item_data.unit_price,
                discount_percent=item_data.discount_percent,
                tva_rate=item_data.tva_rate,
                fodec_rate=item_data.fodec_rate,
                subtotal=totals["subtotal"],
                tva_amount=totals["tva_amount"],
                fodec_amount=totals["fodec_amount"],
                total=totals["total"],
                sort_order=i,
            )
            db.add(item)
            total_subtotal += totals["subtotal"]
            total_tva += totals["tva_amount"]
            total_fodec += totals["fodec_amount"]
            discount = item_data.quantity * item_data.unit_price * (item_data.discount_percent / 100)
            total_discount += discount

        timbre = data.timbre_fiscal if data.timbre_fiscal is not None else invoice.timbre_fiscal
        invoice.subtotal = round(total_subtotal, 3)
        invoice.discount_amount = round(total_discount, 3)
        invoice.tva_amount = round(total_tva, 3)
        invoice.fodec_amount = round(total_fodec, 3)
        invoice.total = round(total_subtotal + total_tva + total_fodec + timbre, 3)
        invoice.balance_due = round(invoice.total - invoice.amount_paid, 3)

    db.commit()
    db.refresh(invoice)

    client = db.query(Client).filter(Client.id == invoice.client_id).first() if invoice.client_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.sort_order).all()

    return InvoiceResponse(
        id=invoice.id,
        reference=invoice.reference,
        invoice_type=invoice.invoice_type,
        status=invoice.status,
        client_id=invoice.client_id,
        client_name=client.name if client else None,
        date=invoice.date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        discount_amount=invoice.discount_amount,
        tva_amount=invoice.tva_amount,
        fodec_amount=invoice.fodec_amount,
        timbre_fiscal=invoice.timbre_fiscal,
        total=invoice.total,
        amount_paid=invoice.amount_paid,
        balance_due=invoice.balance_due,
        currency=invoice.currency,
        notes=invoice.notes,
        conditions=invoice.conditions,
        items=items,
        created_at=invoice.created_at,
    )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer une facture."""
    company = get_user_company(db, current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.company_id == company.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    db.delete(invoice)
    db.commit()


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger la facture en PDF."""
    from app.utils.pdf_generator import generate_invoice_pdf

    company = get_user_company(db, current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.company_id == company.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    client_obj = db.query(Client).filter(Client.id == invoice.client_id).first() if invoice.client_id else None
    supplier_obj = db.query(Supplier).filter(Supplier.id == invoice.supplier_id).first() if invoice.supplier_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.sort_order).all()

    pdf_bytes = generate_invoice_pdf(invoice, company, client_obj or supplier_obj, items)
    filename = f"{invoice.reference}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{invoice_id}/xml")
def download_invoice_xml(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Télécharger la facture en XML."""
    from app.utils.pdf_generator import generate_invoice_xml

    company = get_user_company(db, current_user)
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id, Invoice.company_id == company.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")

    client_obj = db.query(Client).filter(Client.id == invoice.client_id).first() if invoice.client_id else None
    supplier_obj = db.query(Supplier).filter(Supplier.id == invoice.supplier_id).first() if invoice.supplier_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).order_by(InvoiceItem.sort_order).all()

    xml_content = generate_invoice_xml(invoice, company, client_obj or supplier_obj, items)
    filename = f"{invoice.reference}.xml"

    return Response(
        content=xml_content.encode('utf-8'),
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )



@router.post("/{invoice_id}/convert", response_model=InvoiceResponse)
def convert_devis_to_facture(
    invoice_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convertir un devis en facture."""
    company = get_user_company(db, current_user)
    devis = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.company_id == company.id,
        Invoice.invoice_type == InvoiceType.DEVIS.value
    ).first()
    if not devis:
        raise HTTPException(status_code=404, detail="Devis non trouvé")

    # Generate facture reference
    reference = generate_reference(db, company, InvoiceType.FACTURE.value)

    # Create new facture from devis
    facture = Invoice(
        company_id=company.id,
        client_id=devis.client_id,
        reference=reference,
        invoice_type=InvoiceType.FACTURE.value,
        date=date.today(),
        due_date=devis.due_date,
        subtotal=devis.subtotal,
        discount_amount=devis.discount_amount,
        tva_amount=devis.tva_amount,
        fodec_amount=devis.fodec_amount,
        timbre_fiscal=devis.timbre_fiscal,
        total=devis.total,
        balance_due=devis.total,
        currency=devis.currency,
        notes=devis.notes,
        conditions=devis.conditions,
        source_invoice_id=devis.id,
    )
    db.add(facture)
    db.flush()

    # Copy items
    devis_items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == devis.id).all()
    for item in devis_items:
        new_item = InvoiceItem(
            invoice_id=facture.id,
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            unit_price=item.unit_price,
            discount_percent=item.discount_percent,
            tva_rate=item.tva_rate,
            fodec_rate=item.fodec_rate,
            subtotal=item.subtotal,
            tva_amount=item.tva_amount,
            fodec_amount=item.fodec_amount,
            total=item.total,
            sort_order=item.sort_order,
        )
        db.add(new_item)

    # Update devis status
    devis.status = InvoiceStatus.ACCEPTE.value
    db.commit()
    db.refresh(facture)

    client = db.query(Client).filter(Client.id == facture.client_id).first() if facture.client_id else None
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == facture.id).order_by(InvoiceItem.sort_order).all()

    return InvoiceResponse(
        id=facture.id,
        reference=facture.reference,
        invoice_type=facture.invoice_type,
        status=facture.status,
        client_id=facture.client_id,
        client_name=client.name if client else None,
        date=facture.date,
        due_date=facture.due_date,
        subtotal=facture.subtotal,
        discount_amount=facture.discount_amount,
        tva_amount=facture.tva_amount,
        fodec_amount=facture.fodec_amount,
        timbre_fiscal=facture.timbre_fiscal,
        total=facture.total,
        amount_paid=facture.amount_paid,
        balance_due=facture.balance_due,
        currency=facture.currency,
        notes=facture.notes,
        conditions=facture.conditions,
        items=items,
        created_at=facture.created_at,
    )
