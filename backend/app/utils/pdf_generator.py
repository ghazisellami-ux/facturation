"""
Générateur de factures PDF pour SIC Facture.
Utilise ReportLab pour produire des factures professionnelles conformes à la législation tunisienne.
"""
import io
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


def generate_invoice_pdf(invoice, company, client, items) -> bytes:
    """Génère un PDF de facture complet avec infos société et client."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=15*mm, bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    style_title = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=22, textColor=colors.HexColor('#1a73e8'), spaceAfter=2*mm)
    style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#5f6368'), spaceAfter=1*mm)
    style_section = ParagraphStyle('Section', parent=styles['Heading2'],
        fontSize=12, textColor=colors.HexColor('#202124'), spaceBefore=6*mm, spaceAfter=3*mm)
    style_body = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#3c4043'), leading=13)
    style_small = ParagraphStyle('Small', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#80868b'))
    style_amount = ParagraphStyle('Amount', parent=styles['Normal'],
        fontSize=9, alignment=TA_RIGHT, textColor=colors.HexColor('#3c4043'))
    style_total_label = ParagraphStyle('TotalLabel', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT, textColor=colors.HexColor('#5f6368'))
    style_total_value = ParagraphStyle('TotalValue', parent=styles['Normal'],
        fontSize=10, alignment=TA_RIGHT, textColor=colors.HexColor('#202124'),
        fontName='Helvetica-Bold')
    style_net = ParagraphStyle('Net', parent=styles['Normal'],
        fontSize=13, alignment=TA_RIGHT, textColor=colors.HexColor('#1a73e8'),
        fontName='Helvetica-Bold')

    # ── HEADER: Company info + Invoice ref ──
    type_label = {
        'facture': 'FACTURE', 'devis': 'DEVIS', 'avoir': 'AVOIR',
        'bon_livraison': 'BON DE LIVRAISON', 'bon_commande': 'BON DE COMMANDE',
        'facture_achat': "FACTURE D'ACHAT",
    }.get(invoice.invoice_type, 'FACTURE')

    company_lines = [f"<b>{company.name}</b>"]
    if company.tax_id:
        company_lines.append(f"MF : {company.tax_id}")
    if company.address:
        company_lines.append(company.address)
    if company.city:
        addr = company.city
        if company.postal_code:
            addr = f"{company.postal_code} {addr}"
        company_lines.append(addr)
    if company.phone:
        company_lines.append(f"Tél : {company.phone}")
    if company.email:
        company_lines.append(company.email)
    company_text = Paragraph("<br/>".join(company_lines), style_body)

    ref_lines = [
        f"<b>{type_label}</b>",
        f"<b>N° {invoice.reference}</b>",
        f"Date : {invoice.date.strftime('%d/%m/%Y') if invoice.date else '—'}",
    ]
    ref_text = Paragraph("<br/>".join(ref_lines), ParagraphStyle('RefRight', parent=style_body, alignment=TA_RIGHT))

    header_table = Table([[company_text, ref_text]], colWidths=[90*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6*mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dadce0')))
    elements.append(Spacer(1, 4*mm))

    # ── CLIENT INFO ──
    if client:
        elements.append(Paragraph("Client :", style_section))
        client_lines = [f"<b>{client.name}</b>"]
        if client.tax_id:
            client_lines.append(f"MF : {client.tax_id}")
        if client.address:
            client_lines.append(client.address)
        if client.city:
            client_lines.append(client.city)
        if client.phone:
            client_lines.append(f"Tél : {client.phone}")
        if client.email:
            client_lines.append(client.email)
        elements.append(Paragraph("<br/>".join(client_lines), style_body))
        elements.append(Spacer(1, 5*mm))

    # ── ITEMS TABLE ──
    elements.append(Paragraph("DÉTAILS", style_section))

    # Table header
    table_data = [[
        Paragraph("<b>#</b>", style_small),
        Paragraph("<b>DESCRIPTION</b>", style_small),
        Paragraph("<b>QTÉ</b>", ParagraphStyle('', parent=style_small, alignment=TA_CENTER)),
        Paragraph("<b>P.U. HT</b>", ParagraphStyle('', parent=style_small, alignment=TA_RIGHT)),
        Paragraph("<b>REM %</b>", ParagraphStyle('', parent=style_small, alignment=TA_CENTER)),
        Paragraph("<b>TVA %</b>", ParagraphStyle('', parent=style_small, alignment=TA_CENTER)),
        Paragraph("<b>TOTAL HT</b>", ParagraphStyle('', parent=style_small, alignment=TA_RIGHT)),
    ]]

    fmt = lambda v: f"{v:,.3f}".replace(",", " ")

    for i, item in enumerate(items, 1):
        table_data.append([
            Paragraph(str(i), style_body),
            Paragraph(item.description or '', style_body),
            Paragraph(str(item.quantity), ParagraphStyle('', parent=style_body, alignment=TA_CENTER)),
            Paragraph(fmt(item.unit_price), style_amount),
            Paragraph(f"{item.discount_percent}%", ParagraphStyle('', parent=style_body, alignment=TA_CENTER)),
            Paragraph(f"{item.tva_rate}%", ParagraphStyle('', parent=style_body, alignment=TA_CENTER)),
            Paragraph(fmt(item.subtotal), style_amount),
        ])

    item_table = Table(table_data, colWidths=[8*mm, 62*mm, 15*mm, 25*mm, 15*mm, 15*mm, 30*mm])
    item_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f3f4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#5f6368')),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        # Body
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        # Grid
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#dadce0')),
        ('LINEBELOW', (0, 1), (-1, -1), 0.3, colors.HexColor('#e8eaed')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(item_table)
    elements.append(Spacer(1, 6*mm))

    # ── TOTALS ──
    totals_data = [
        [Paragraph("Total HT", style_total_label), Paragraph(f"{fmt(invoice.subtotal)} TND", style_total_value)],
    ]
    if invoice.discount_amount > 0:
        totals_data.append([
            Paragraph("Remise", style_total_label),
            Paragraph(f"-{fmt(invoice.discount_amount)} TND", style_total_value),
        ])
    if invoice.fodec_amount > 0:
        totals_data.append([
            Paragraph("FODEC", style_total_label),
            Paragraph(f"{fmt(invoice.fodec_amount)} TND", style_total_value),
        ])
    totals_data.append([
        Paragraph("TVA", style_total_label),
        Paragraph(f"{fmt(invoice.tva_amount)} TND", style_total_value),
    ])
    totals_data.append([
        Paragraph("Timbre fiscal", style_total_label),
        Paragraph(f"{fmt(invoice.timbre_fiscal)} TND", style_total_value),
    ])
    totals_data.append([
        Paragraph("<b>Net à payer</b>", ParagraphStyle('', parent=style_total_label, fontName='Helvetica-Bold',
                                                        textColor=colors.HexColor('#1a73e8'))),
        Paragraph(f"<b>{fmt(invoice.total)} TND</b>", style_net),
    ])

    totals_table = Table(totals_data, colWidths=[120*mm, 50*mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#1a73e8')),
        ('TOPPADDING', (0, -1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(totals_table)

    # ── NOTES / CONDITIONS ──
    if invoice.notes:
        elements.append(Spacer(1, 8*mm))
        elements.append(Paragraph("NOTES", style_section))
        elements.append(Paragraph(invoice.notes, style_body))

    if invoice.conditions:
        elements.append(Spacer(1, 4*mm))
        elements.append(Paragraph("CONDITIONS", style_section))
        elements.append(Paragraph(invoice.conditions, style_body))

    # ── FOOTER (rendered at absolute bottom of every page) ──
    footer_text = f"Généré par SIC Facture — {company.name}"
    if company.tax_id:
        footer_text += f" — MF : {company.tax_id}"

    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(colors.HexColor('#80868b'))
        canvas_obj.drawCentredString(A4[0] / 2, 12*mm, footer_text)
        # Thin line above footer
        canvas_obj.setStrokeColor(colors.HexColor('#dadce0'))
        canvas_obj.setLineWidth(0.3)
        canvas_obj.line(20*mm, 15*mm, A4[0] - 20*mm, 15*mm)
        canvas_obj.restoreState()

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_invoice_xml(invoice, company, client, items) -> str:
    """Génère un XML de facture (format e-facture simplifié)."""
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
    # Remove extra xml declaration from toprettyxml
    lines = pretty.split('\n')
    return '\n'.join(lines)
