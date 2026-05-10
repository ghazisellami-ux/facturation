"""
Générateur de factures PDF pour SIC Facture.
Utilise fpdf2 pour produire des factures professionnelles conformes à la législation tunisienne.
"""
import io
import os
import tempfile
import urllib.request
from fpdf import FPDF
from app.utils.amount_words import amount_to_words


class InvoicePDF(FPDF):
    """PDF personnalisé avec en-tête et pied de page."""

    def __init__(self, company, invoice_type_label):
        super().__init__()
        self.company = company
        self.invoice_type_label = invoice_type_label
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        # Logo si disponible
        logo_path = self._get_logo_path()
        if logo_path:
            self.image(logo_path, 10, 8, 35)
            self.set_xy(50, 10)
        else:
            self.set_xy(10, 10)

        # Nom de l'entreprise
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, self.company.name, ln=True)

        # Infos entreprise
        self.set_font('Helvetica', '', 8)
        self.set_text_color(0, 0, 0)
        x_start = 50 if logo_path else 10
        self.set_x(x_start)
        info_parts = []
        if self.company.tax_id:
            info_parts.append(f"MF : {self.company.tax_id}")
        if hasattr(self.company, 'rne') and self.company.rne:
            info_parts.append(f"RNE : {self.company.rne}")
        if self.company.address:
            info_parts.append(self.company.address)
        if self.company.city:
            city = self.company.city
            if self.company.postal_code:
                city = f"{self.company.postal_code} {city}"
            info_parts.append(city)
        if self.company.phone:
            info_parts.append(f"Tel : {self.company.phone}")
        if self.company.email:
            info_parts.append(self.company.email)

        for part in info_parts:
            self.cell(0, 4, part, ln=True)
            self.set_x(x_start)

        self.ln(3)
        # Ligne séparatrice
        self.set_draw_color(218, 220, 224)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(218, 220, 224)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(0, 0, 0)
        footer = f"Genere par SIC Facture - {self.company.name}"
        if self.company.tax_id:
            footer += f" - MF : {self.company.tax_id}"
        if hasattr(self.company, 'rne') and self.company.rne:
            footer += f" - RNE : {self.company.rne}"
        self.cell(0, 5, footer, align='C')

    def _get_logo_path(self):
        """Tente de charger le logo de l'entreprise."""
        if hasattr(self.company, 'logo_url') and self.company.logo_url:
            try:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                urllib.request.urlretrieve(self.company.logo_url, tmp.name)
                return tmp.name
            except Exception:
                pass
        # Chercher le logo local
        logo_local = os.path.join(os.path.dirname(__file__), '..', '..', 'logo-sic.jpg')
        if os.path.exists(logo_local):
            return logo_local
        return None


def generate_invoice_pdf(invoice, company, client, items) -> bytes:
    """Genere un PDF de facture complet avec infos societe et client."""

    type_label = {
        'facture': 'FACTURE', 'devis': 'DEVIS', 'avoir': 'AVOIR',
        'bon_livraison': 'BON DE LIVRAISON', 'bon_commande': 'BON DE COMMANDE',
        'facture_achat': "FACTURE D'ACHAT",
    }.get(invoice.invoice_type, 'FACTURE')

    pdf = InvoicePDF(company, type_label)
    pdf.add_page()

    # ── TYPE & REFERENCE ──
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"{type_label}  N. {invoice.reference}", ln=True, align='R')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 0, 0)
    date_str = invoice.date.strftime('%d/%m/%Y') if invoice.date else '-'
    pdf.cell(0, 5, f"Date : {date_str}", ln=True, align='R')
    if invoice.due_date:
        pdf.cell(0, 5, f"Echeance : {invoice.due_date.strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(5)

    # ── CLIENT ──
    if client:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, 'Client :', ln=True)

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 5, client.name, ln=True)

        pdf.set_font('Helvetica', '', 8)
        if hasattr(client, 'tax_id') and client.tax_id:
            pdf.cell(0, 4, f"MF : {client.tax_id}", ln=True)
        if hasattr(client, 'rne') and client.rne:
            pdf.cell(0, 4, f"RNE : {client.rne}", ln=True)
        if hasattr(client, 'address') and client.address:
            pdf.cell(0, 4, client.address, ln=True)
        if hasattr(client, 'city') and client.city:
            pdf.cell(0, 4, client.city, ln=True)
        if hasattr(client, 'phone') and client.phone:
            pdf.cell(0, 4, f"Tel : {client.phone}", ln=True)
        if hasattr(client, 'email') and client.email:
            pdf.cell(0, 4, client.email, ln=True)
        if hasattr(client, 'contact_name') and client.contact_name:
            pdf.cell(0, 4, f"Contact : {client.contact_name}", ln=True)
        pdf.ln(5)

    # ── TABLE DES ARTICLES ──
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(32, 33, 36)
    pdf.cell(0, 7, 'DETAILS', ln=True)
    pdf.ln(2)

    # En-tête du tableau
    col_widths = [10, 70, 18, 25, 18, 18, 31]
    headers = ['#', 'DESCRIPTION', 'QTE', 'P.U. HT', 'REM %', 'TVA %', 'TOTAL HT']

    pdf.set_fill_color(241, 243, 244)
    pdf.set_draw_color(218, 220, 224)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(0, 0, 0)

    for i, (w, h) in enumerate(zip(col_widths, headers)):
        align = 'C' if i in (2, 4, 5) else ('R' if i in (3, 6) else 'L')
        pdf.cell(w, 7, h, border=0, align=align, fill=True)
    pdf.ln()
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    # Lignes d'articles
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(0, 0, 0)

    fmt = lambda v: f"{v:,.3f}".replace(",", " ")

    for idx, item in enumerate(items, 1):
        y_before = pdf.get_y()

        pdf.cell(col_widths[0], 6, str(idx), align='L')
        pdf.cell(col_widths[1], 6, (item.description or '')[:55], align='L')
        pdf.cell(col_widths[2], 6, str(item.quantity), align='C')
        pdf.cell(col_widths[3], 6, fmt(item.unit_price), align='R')
        pdf.cell(col_widths[4], 6, f"{item.discount_percent}%", align='C')
        pdf.cell(col_widths[5], 6, f"{item.tva_rate}%", align='C')
        pdf.cell(col_widths[6], 6, fmt(item.subtotal), align='R')
        pdf.ln()

        # Ligne de séparation fine
        pdf.set_draw_color(232, 234, 237)
        pdf.set_line_width(0.15)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(5)

    # ── TOTAUX ──
    x_label = 120
    x_value = 165
    w_label = 45
    w_value = 35

    def add_total_line(label, value, bold=False, color=(0, 0, 0)):
        pdf.set_text_color(0, 0, 0)
        if bold:
            pdf.set_font('Helvetica', 'B', 10)
        else:
            pdf.set_font('Helvetica', '', 9)
        pdf.set_x(x_label)
        pdf.cell(w_label, 6, label, align='R')
        pdf.cell(w_value, 6, value, align='R', ln=True)

    add_total_line('Total HT', f"{fmt(invoice.subtotal)} TND")

    if invoice.discount_amount > 0:
        add_total_line('Remise', f"-{fmt(invoice.discount_amount)} TND")

    if invoice.fodec_amount > 0:
        add_total_line('FODEC', f"{fmt(invoice.fodec_amount)} TND")

    add_total_line('TVA', f"{fmt(invoice.tva_amount)} TND")
    add_total_line('Timbre fiscal', f"{fmt(invoice.timbre_fiscal)} TND")

    # Ligne séparatrice avant net à payer
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(x_label, pdf.get_y() + 1, 200, pdf.get_y() + 1)
    pdf.ln(3)

    add_total_line('Net a payer', f"{fmt(invoice.total)} TND", bold=True, color=(0, 0, 0))

    # ── MONTANT EN LETTRES ──
    pdf.ln(6)
    pdf.set_draw_color(218, 220, 224)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(0, 0, 0)
    words = amount_to_words(invoice.total)
    pdf.multi_cell(0, 5, f"Arretee la presente facture a la somme de : {words}.")

    # ── NOTES ──
    if invoice.notes:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, 'NOTES', ln=True)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 4, invoice.notes)

    if invoice.conditions:
        pdf.ln(4)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, 'CONDITIONS', ln=True)
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 4, invoice.conditions)

    # Output
    return pdf.output()


def generate_invoice_xml(invoice, company, client, items) -> str:
    """Genere un XML de facture (format e-facture simplifie)."""
    import xml.etree.ElementTree as ET
    from xml.dom.minidom import parseString

    root = ET.Element("Facture")
    root.set("xmlns", "urn:sic:facture:1.0")

    # Document info
    doc_el = ET.SubElement(root, "Document")
    ET.SubElement(doc_el, "Type").text = invoice.invoice_type
    ET.SubElement(doc_el, "Reference").text = invoice.reference
    ET.SubElement(doc_el, "Date").text = invoice.date.isoformat() if invoice.date else ""
    if invoice.due_date:
        ET.SubElement(doc_el, "DateEcheance").text = invoice.due_date.isoformat()
    ET.SubElement(doc_el, "Statut").text = invoice.status
    ET.SubElement(doc_el, "Devise").text = invoice.currency

    # Emetteur (Company)
    emetteur = ET.SubElement(root, "Emetteur")
    ET.SubElement(emetteur, "Nom").text = company.name
    ET.SubElement(emetteur, "MatriculeFiscal").text = company.tax_id or ""
    ET.SubElement(emetteur, "Adresse").text = company.address or ""
    ET.SubElement(emetteur, "Ville").text = company.city or ""
    ET.SubElement(emetteur, "CodePostal").text = company.postal_code or ""
    ET.SubElement(emetteur, "Telephone").text = company.phone or ""
    ET.SubElement(emetteur, "Email").text = company.email or ""

    # Destinataire (Client)
    if client:
        dest = ET.SubElement(root, "Destinataire")
        ET.SubElement(dest, "Nom").text = client.name
        ET.SubElement(dest, "MatriculeFiscal").text = client.tax_id or ""
        ET.SubElement(dest, "Adresse").text = client.address or ""
        ET.SubElement(dest, "Ville").text = client.city or ""
        ET.SubElement(dest, "Telephone").text = client.phone or ""
        ET.SubElement(dest, "Email").text = client.email or ""

    # Lignes
    lignes = ET.SubElement(root, "Lignes")
    for item in items:
        ligne = ET.SubElement(lignes, "Ligne")
        ET.SubElement(ligne, "Description").text = item.description
        ET.SubElement(ligne, "Quantite").text = str(item.quantity)
        ET.SubElement(ligne, "Unite").text = item.unit
        ET.SubElement(ligne, "PrixUnitaireHT").text = f"{item.unit_price:.3f}"
        ET.SubElement(ligne, "RemisePourcent").text = f"{item.discount_percent:.2f}"
        ET.SubElement(ligne, "TauxTVA").text = f"{item.tva_rate:.2f}"
        ET.SubElement(ligne, "TauxFODEC").text = f"{item.fodec_rate:.2f}"
        ET.SubElement(ligne, "MontantHT").text = f"{item.subtotal:.3f}"
        ET.SubElement(ligne, "MontantTVA").text = f"{item.tva_amount:.3f}"
        ET.SubElement(ligne, "MontantTTC").text = f"{item.total:.3f}"

    # Totaux
    totaux = ET.SubElement(root, "Totaux")
    ET.SubElement(totaux, "TotalHT").text = f"{invoice.subtotal:.3f}"
    ET.SubElement(totaux, "TotalRemise").text = f"{invoice.discount_amount:.3f}"
    ET.SubElement(totaux, "TotalFODEC").text = f"{invoice.fodec_amount:.3f}"
    ET.SubElement(totaux, "TotalTVA").text = f"{invoice.tva_amount:.3f}"
    ET.SubElement(totaux, "TimbreFiscal").text = f"{invoice.timbre_fiscal:.3f}"
    ET.SubElement(totaux, "NetAPayer").text = f"{invoice.total:.3f}"

    xml_str = ET.tostring(root, encoding='unicode', xml_declaration=False)
    pretty = parseString(f'<?xml version="1.0" encoding="UTF-8"?>{xml_str}').toprettyxml(indent="  ")
    lines = pretty.split('\n')
    return '\n'.join(lines)
