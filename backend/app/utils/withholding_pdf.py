"""
Générateur de Certificat de Retenue à la Source - Format officiel tunisien.
Conforme au format du Ministère des Finances de la République Tunisienne.
"""
import io
from fpdf import FPDF


def fmt(n: float) -> str:
    """Format number with 3 decimals and space separator."""
    return f"{n:,.3f}".replace(",", " ").replace(".", ",").replace(" ", " ")


class WithholdingCertificatePDF(FPDF):
    """PDF du certificat de retenue à la source."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def _cell_bordered(self, w, h, txt, align="L", bold=False, bg=False, size=9):
        if bold:
            self.set_font("Helvetica", "B", size)
        else:
            self.set_font("Helvetica", "", size)
        if bg:
            self.set_fill_color(220, 230, 241)
            self.cell(w, h, txt, border=1, align=align, fill=True)
        else:
            self.cell(w, h, txt, border=1, align=align)


def generate_withholding_pdf(withholding, company, client_or_supplier) -> bytes:
    """
    Generate a Certificat de Retenue à la Source PDF.
    
    Args:
        withholding: WithholdingTax model instance
        company: Company model instance (payeur)
        client_or_supplier: Client or Supplier model instance (bénéficiaire)
    """
    pdf = WithholdingCertificatePDF()
    pdf.add_page()
    pw = pdf.w - 20  # page width minus margins

    # ── Header ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(pw, 7, "REPUBLIQUE TUNISIENNE", ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(pw, 7, "MINISTERE DES FINANCES", ln=True)
    pdf.ln(10)

    # ── Title ──
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(pw, 5,
        "CERTIFICAT DE RETENUE A LA SOURCE\n"
        "AU TITRE DE LA TVA ET DE L'IMPOT SUR LE REVENU OU DE L'IMPOT SUR LES SOCIETES",
        align="C"
    )
    pdf.ln(8)

    # ── Reference ──
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(220, 230, 241)
    pdf.cell(40, 7, "  Reference", border=1, fill=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(pw - 40, 7, f"  {withholding.id}", border=1, ln=True)
    pdf.ln(4)

    # ── Info row ──
    date_str = withholding.date.strftime("%d-%m-%Y") if withholding.date else ""
    year_str = str(withholding.date.year) if withholding.date else ""
    ref_str = withholding.reference or ""

    col_w = pw / 4
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(220, 230, 241)
    pdf.cell(col_w, 6, "Date", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "N. chez le declarant", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Exercice de facturation", border=1, align="C", fill=True)
    pdf.cell(col_w, 6, "Date de paiement", border=1, align="C", fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(col_w, 7, date_str, border=1, align="C")
    pdf.cell(col_w, 7, ref_str, border=1, align="C")
    pdf.cell(col_w, 7, year_str, border=1, align="C")
    pdf.cell(col_w, 7, date_str, border=1, align="C")
    pdf.ln(10)

    # ── Personne ou organisme Payeur ──
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(220, 230, 241)
    pdf.cell(pw, 7, "Personne ou organisme Payeur", border=1, align="C", fill=True, ln=True)

    label_w = 55
    val_w = pw - label_w

    rows = [
        ("Type identifiant", "Matricule fiscal"),
        ("Identifiant", company.tax_id or ""),
        ("Nom et prenom ou raison sociale", company.name or ""),
        ("Adresse", f"{company.address or ''} {company.city or ''} {company.postal_code or ''}".strip()),
        ("RNE", company.rne or ""),
    ]
    for label, val in rows:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(label_w, 6, f"  {label}", border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(val_w, 6, f"  {val}", border=1, ln=True)

    pdf.ln(6)

    # ── Bénéficiaire ──
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(220, 230, 241)

    if withholding.type == "emise":
        pdf.cell(pw, 7, "Beneficiaire (Fournisseur)", border=1, align="C", fill=True, ln=True)
    else:
        pdf.cell(pw, 7, "Beneficiaire (Client)", border=1, align="C", fill=True, ln=True)

    ben_name = ""
    ben_tax_id = ""
    ben_address = ""
    ben_rne = ""

    if client_or_supplier:
        ben_name = getattr(client_or_supplier, "name", "") or ""
        ben_tax_id = getattr(client_or_supplier, "tax_id", "") or ""
        address_parts = []
        if getattr(client_or_supplier, "address", None):
            address_parts.append(client_or_supplier.address)
        if getattr(client_or_supplier, "city", None):
            address_parts.append(client_or_supplier.city)
        if getattr(client_or_supplier, "postal_code", None):
            address_parts.append(client_or_supplier.postal_code)
        ben_address = " ".join(address_parts)
        ben_rne = getattr(client_or_supplier, "rne", "") or ""
    else:
        ben_name = withholding.beneficiary_name or ""
        ben_tax_id = withholding.beneficiary_tax_id or ""

    ben_rows = [
        ("Type identifiant", "Matricule fiscal"),
        ("Identifiant", ben_tax_id),
        ("Nom et prenom ou raison sociale", ben_name),
        ("Adresse", ben_address),
        ("RNE", ben_rne),
    ]
    for label, val in ben_rows:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(label_w, 6, f"  {label}", border=1)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(val_w, 6, f"  {val}", border=1, ln=True)

    pdf.ln(8)

    # ── Tableau de détails ──
    base_ht = withholding.base_amount or 0
    rate = withholding.rate or 0
    tva_rate = 19.0  # default TVA rate
    tva_due = round(base_ht * tva_rate / 100, 3)
    total_ttc = round(base_ht + tva_due, 3)
    tva_retenue = 0  # TVA retenue à la source (usually 0)
    montant_retenue = withholding.tax_amount or round(base_ht * rate / 100, 3)
    montant_servi = round(total_ttc - montant_retenue, 3)

    # Header row
    cols = [
        ("Nature de l'operation", 42),
        ("Montants\nHors TVA", 22),
        ("TVA due", 20),
        ("Montant total\nTVA comprise", 24),
        ("TVA retenue\na la source", 22),
        ("Taux de la\nretenue", 18),
        ("Montant de\nla retenue", 22),
        ("Montant\nservi", 22),
    ]
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(220, 230, 241)
    y0 = pdf.get_y()
    x0 = pdf.get_x()
    max_h = 12

    for label, w in cols:
        x = pdf.get_x()
        pdf.rect(x, y0, w, max_h)
        pdf.set_fill_color(220, 230, 241)
        pdf.rect(x, y0, w, max_h, "F")
        pdf.rect(x, y0, w, max_h, "D")
        # Center text in cell
        lines = label.split("\n")
        line_h = max_h / (len(lines) + 1)
        for li, line in enumerate(lines):
            pdf.set_xy(x, y0 + line_h * (li + 0.5))
            pdf.cell(w, line_h, line, align="C")
        pdf.set_xy(x + w, y0)

    pdf.set_xy(x0, y0 + max_h)

    # Data row
    pdf.set_font("Helvetica", "", 8)
    note_text = withholding.notes or "Retenue a la source"
    row_h = 14

    data_vals = [
        (note_text, 42, "L"),
        (fmt(base_ht), 22, "R"),
        (fmt(tva_due), 20, "R"),
        (fmt(total_ttc), 24, "R"),
        (str(int(tva_retenue)), 22, "R"),
        (str(rate), 18, "C"),
        (fmt(montant_retenue), 22, "R"),
        (fmt(montant_servi), 22, "R"),
    ]

    y1 = pdf.get_y()
    for val, w, align in data_vals:
        x = pdf.get_x()
        pdf.rect(x, y1, w, row_h)
        if w == 42:
            # Multi-line note
            pdf.set_xy(x + 1, y1 + 1)
            pdf.set_font("Helvetica", "", 7)
            pdf.multi_cell(w - 2, 3.5, val)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_xy(x + w, y1)
        else:
            pdf.set_xy(x, y1 + (row_h - 4) / 2)
            pdf.cell(w, 4, f" {val} ", align=align)
            pdf.set_xy(x + w, y1)

    pdf.set_xy(x0, y1 + row_h)

    # Total row
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(240, 240, 240)
    total_cols = [
        ("Total", 42, "C"),
        ("", 22, "C"),
        ("", 20, "C"),
        (fmt(total_ttc), 24, "R"),
        ("", 22, "C"),
        ("", 18, "C"),
        (fmt(montant_retenue), 22, "R"),
        (fmt(montant_servi), 22, "R"),
    ]
    for val, w, align in total_cols:
        pdf.cell(w, 7, f" {val} ", border=1, align=align, fill=True)
    pdf.ln(12)

    # ── Footer note ──
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(pw, 5, f"Document genere par SIC Facture - {company.name}", align="C")

    # Output
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def generate_withholding_xml(withholding, company, client_or_supplier) -> str:
    """
    Generate an XML representation of the withholding certificate.
    Compatible with Tunisian tax authority format.
    """
    base_ht = withholding.base_amount or 0
    rate = withholding.rate or 0
    tva_rate = 19.0
    tva_due = round(base_ht * tva_rate / 100, 3)
    total_ttc = round(base_ht + tva_due, 3)
    montant_retenue = withholding.tax_amount or round(base_ht * rate / 100, 3)
    montant_servi = round(total_ttc - montant_retenue, 3)
    date_str = withholding.date.strftime("%Y-%m-%d") if withholding.date else ""
    year_str = str(withholding.date.year) if withholding.date else ""

    ben_name = ""
    ben_tax_id = ""
    ben_address = ""
    if client_or_supplier:
        ben_name = getattr(client_or_supplier, "name", "") or ""
        ben_tax_id = getattr(client_or_supplier, "tax_id", "") or ""
        address_parts = []
        if getattr(client_or_supplier, "address", None):
            address_parts.append(client_or_supplier.address)
        if getattr(client_or_supplier, "city", None):
            address_parts.append(client_or_supplier.city)
        ben_address = " ".join(address_parts)
    else:
        ben_name = withholding.beneficiary_name or ""
        ben_tax_id = withholding.beneficiary_tax_id or ""

    def esc(s):
        """Escape XML special characters."""
        return (str(s or "")
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<CertificatRetenueSource>
  <Reference>{esc(withholding.id)}</Reference>
  <Date>{date_str}</Date>
  <Exercice>{year_str}</Exercice>
  <DatePaiement>{date_str}</DatePaiement>
  <NumeroDeclarant>{esc(withholding.reference)}</NumeroDeclarant>
  <Type>{esc(withholding.type)}</Type>

  <Payeur>
    <TypeIdentifiant>Matricule fiscal</TypeIdentifiant>
    <Identifiant>{esc(company.tax_id)}</Identifiant>
    <RaisonSociale>{esc(company.name)}</RaisonSociale>
    <Adresse>{esc((company.address or '') + ' ' + (company.city or '') + ' ' + (company.postal_code or ''))}</Adresse>
    <RNE>{esc(company.rne)}</RNE>
  </Payeur>

  <Beneficiaire>
    <TypeIdentifiant>Matricule fiscal</TypeIdentifiant>
    <Identifiant>{esc(ben_tax_id)}</Identifiant>
    <RaisonSociale>{esc(ben_name)}</RaisonSociale>
    <Adresse>{esc(ben_address)}</Adresse>
  </Beneficiaire>

  <DetailOperation>
    <NatureOperation>{esc(withholding.notes or 'Retenue a la source')}</NatureOperation>
    <MontantHorsTVA>{base_ht:.3f}</MontantHorsTVA>
    <TVADue>{tva_due:.3f}</TVADue>
    <MontantTotalTVAComprise>{total_ttc:.3f}</MontantTotalTVAComprise>
    <TVARetenueSource>0.000</TVARetenueSource>
    <TauxRetenue>{rate}</TauxRetenue>
    <MontantRetenue>{montant_retenue:.3f}</MontantRetenue>
    <MontantServi>{montant_servi:.3f}</MontantServi>
  </DetailOperation>

  <Totaux>
    <TotalTTC>{total_ttc:.3f}</TotalTTC>
    <TotalRetenue>{montant_retenue:.3f}</TotalRetenue>
    <TotalServi>{montant_servi:.3f}</TotalServi>
  </Totaux>
</CertificatRetenueSource>"""

    return xml
