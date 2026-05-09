import sys
sys.path.insert(0, '.')
from app.database import engine
from sqlalchemy import text

LOCAL_COMPANY = 'f38a5617-f275-49f6-a837-7de881cf3fb3'

with engine.connect() as conn:
    # Get company info
    r = conn.execute(text("SELECT name, tax_id, email, phone, address, city, postal_code, country, currency FROM companies WHERE id = :id"), {"id": LOCAL_COMPANY}).fetchone()
    if r:
        print(f"COMPANY|{r[0]}|{r[1]}|{r[2]}|{r[3]}|{r[4]}|{r[5]}|{r[6]}|{r[7]}|{r[8]}")
    
    # Get clients
    rows = conn.execute(text("SELECT id, name, tax_id, email, phone, address, city, postal_code, country, contact_name, notes, balance FROM clients WHERE company_id = :cid"), {"cid": LOCAL_COMPANY}).fetchall()
    for r in rows:
        print(f"CLIENT|{'|'.join(str(x) if x is not None else '' for x in r)}")
    
    # Get suppliers
    rows = conn.execute(text("SELECT id, name, tax_id, email, phone, address, city, postal_code, country, contact_name, notes, balance FROM suppliers WHERE company_id = :cid"), {"cid": LOCAL_COMPANY}).fetchall()
    for r in rows:
        print(f"SUPPLIER|{'|'.join(str(x) if x is not None else '' for x in r)}")
    
    # Get invoices
    rows = conn.execute(text("SELECT id, client_id, reference, invoice_type, status, date, due_date, subtotal, discount_amount, tva_amount, fodec_amount, timbre_fiscal, total, amount_paid, balance_due, currency, notes, conditions, footer_note, source_invoice_id, supplier_id FROM invoices WHERE company_id = :cid"), {"cid": LOCAL_COMPANY}).fetchall()
    for r in rows:
        print(f"INVOICE|{'|'.join(str(x) if x is not None else '' for x in r)}")
    
    # Get invoice items
    rows = conn.execute(text("SELECT ii.id, ii.invoice_id, ii.product_id, ii.description, ii.quantity, ii.unit, ii.unit_price, ii.discount_percent, ii.tva_rate, ii.fodec_rate, ii.line_total FROM invoice_items ii JOIN invoices i ON ii.invoice_id = i.id WHERE i.company_id = :cid"), {"cid": LOCAL_COMPANY}).fetchall()
    for r in rows:
        print(f"ITEM|{'|'.join(str(x) if x is not None else '' for x in r)}")

print("EXPORT_DONE")
