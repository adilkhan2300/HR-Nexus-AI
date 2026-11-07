"""
HR Nexus AI - Document Generation Service
Generates professional enterprise PDFs (ReportLab) and DOCX (python-docx) files:
- Offer Letters
- Appointment Letters
- Confidentiality Agreements (NDA)
- Joining Instructions & Document Checklists
"""
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from config import GENERATED_DOCS_DIR

def generate_offer_letter_pdf(offer_data: dict) -> Path:
    """Generate high quality enterprise Offer Letter PDF."""
    offer_code = offer_data.get('offer_code', 'OFF-GEN')
    filename = f"Offer_Letter_{offer_code}_{offer_data.get('candidate_name', 'Candidate').replace(' ', '_')}.pdf"
    file_path = GENERATED_DOCS_DIR / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()

    # Custom styles
    brand_style = ParagraphStyle('Brand', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#1e3a8a'))
    subbrand_style = ParagraphStyle('SubBrand', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748b'))
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading2'], fontSize=15, leading=19, textColor=colors.HexColor('#0f172a'), alignment=1, spaceBefore=10, spaceAfter=15)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'))
    bold_style = ParagraphStyle('BoldText', parent=body_style, fontName='Helvetica-Bold')

    story = []

    # Header / Branding
    story.append(Paragraph("<b>HR NEXUS ENTERPRISES INC.</b>", brand_style))
    story.append(Paragraph("100 Innovation Boulevard, Tech District | contact@hrnexus.ai | www.hrnexus.ai", subbrand_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))

    # Reference Details
    date_str = datetime.now().strftime("%B %d, %Y")
    meta_data = [
        [Paragraph(f"<b>Date:</b> {date_str}", body_style), Paragraph(f"<b>Offer Ref:</b> {offer_code}", body_style)],
        [Paragraph(f"<b>Candidate:</b> {offer_data.get('candidate_name')}", body_style), Paragraph(f"<b>Email:</b> {offer_data.get('candidate_email')}", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_meta)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>FORMAL OFFER OF EMPLOYMENT</b>", title_style))

    p1 = (
        f"Dear {offer_data.get('candidate_name')},<br/><br/>"
        f"We are delighted to extend you an offer of employment with <b>HR Nexus Enterprises Inc.</b> "
        f"We were immensely impressed by your experience and competencies during the evaluation process, and we believe "
        f"you will make an outstanding addition to our team."
    )
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 12))

    # Offer Details Table
    details_table_data = [
        [Paragraph("<b>Role & Designation:</b>", bold_style), Paragraph(offer_data.get('designation', 'Specialist'), body_style)],
        [Paragraph("<b>Department:</b>", bold_style), Paragraph(offer_data.get('department', 'Operations'), body_style)],
        [Paragraph("<b>Reporting Manager:</b>", bold_style), Paragraph(offer_data.get('reporting_manager', 'Department Head'), body_style)],
        [Paragraph("<b>Proposed Joining Date:</b>", bold_style), Paragraph(str(offer_data.get('joining_date', 'Immediate')), body_style)],
        [Paragraph("<b>Work Location:</b>", bold_style), Paragraph(offer_data.get('work_location', 'Hybrid'), body_style)],
        [Paragraph("<b>Employment Type:</b>", bold_style), Paragraph(offer_data.get('employment_type', 'Full-Time Regular'), body_style)],
        [Paragraph("<b>Annual Base Compensation:</b>", bold_style), Paragraph(f"<b>${offer_data.get('annual_ctc', 0):,.2f} {offer_data.get('currency', 'USD')}</b>", bold_style)]
    ]
    t_details = Table(details_table_data, colWidths=[180, 340])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_details)
    story.append(Spacer(1, 12))

    # Terms & Conditions
    terms = (
        "<b>Terms and Conditions of Employment:</b><br/>"
        "1. <b>Probation Period:</b> Employment is subject to a 90-day probationary period from your joining date.<br/>"
        "2. <b>Statutory Documents:</b> This offer is contingent upon successful verification of identity, prior employment credentials, and educational degrees.<br/>"
        "3. <b>Benefits:</b> Comprehensive medical, dental, and vision insurance coverage takes effect on your first day. You accrue 20 paid annual leave days.<br/>"
        "4. <b>Confidentiality:</b> You agree to execute standard Proprietary Information and Inventions Agreement prior to day one."
    )
    story.append(Paragraph(terms, body_style))
    story.append(Spacer(1, 25))

    # Signatures
    sig_data = [
        [
            Paragraph("<b>For HR Nexus Enterprises Inc.</b><br/><br/><br/>___________________________<br/>Authorized HR Signatory<br/>Chief People Officer", body_style),
            Paragraph("<b>Candidate Acceptance</b><br/><br/><br/>___________________________<br/>Candidate Signature<br/>Date: ____________________", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260])
    t_sig.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_sig)

    doc.build(story)
    return file_path

def generate_offer_letter_docx(offer_data: dict) -> Path:
    """Generate Word DOCX Offer Letter."""
    offer_code = offer_data.get('offer_code', 'OFF-GEN')
    filename = f"Offer_Letter_{offer_code}_{offer_data.get('candidate_name', 'Candidate').replace(' ', '_')}.docx"
    file_path = GENERATED_DOCS_DIR / filename

    doc = Document()
    doc.add_heading("HR NEXUS ENTERPRISES INC.", level=0)
    p_sub = doc.add_paragraph("100 Innovation Boulevard | contact@hrnexus.ai | www.hrnexus.ai")
    p_sub.runs[0].font.color.rgb = RGBColor(100, 116, 139)

    doc.add_heading("FORMAL OFFER OF EMPLOYMENT", level=2)

    doc.add_paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    doc.add_paragraph(f"Offer Reference Code: {offer_code}")
    doc.add_paragraph(f"To: {offer_data.get('candidate_name')} ({offer_data.get('candidate_email')})")

    doc.add_paragraph(
        f"Dear {offer_data.get('candidate_name')},\n\n"
        f"We are thrilled to offer you the position of {offer_data.get('designation')} in our "
        f"{offer_data.get('department')} department at HR Nexus Enterprises Inc."
    )

    table = doc.add_table(rows=7, cols=2)
    table.style = 'Light Shading Accent 1'
    rows = [
        ("Designation", offer_data.get('designation', '')),
        ("Department", offer_data.get('department', '')),
        ("Reporting Manager", offer_data.get('reporting_manager', '')),
        ("Joining Date", str(offer_data.get('joining_date', ''))),
        ("Work Location", offer_data.get('work_location', '')),
        ("Employment Type", offer_data.get('employment_type', '')),
        ("Annual Compensation", f"${offer_data.get('annual_ctc', 0):,.2f} {offer_data.get('currency', 'USD')}")
    ]
    for i, (k, v) in enumerate(rows):
        table.rows[i].cells[0].text = k
        table.rows[i].cells[1].text = str(v)

    doc.add_heading("Terms and Conditions", level=3)
    doc.add_paragraph(
        "1. This appointment is subject to satisfactory verification of credentials and background references.\n"
        "2. A standard 90-day probationary period will apply.\n"
        "3. You will receive 20 days of paid annual leave plus statutory holidays."
    )

    doc.add_paragraph("\nSincerely,\nHR Nexus AI Talent Operations\n\nAccepted by Candidate:\n\nSignature: ______________________ Date: ______________")
    doc.save(str(file_path))
    return file_path

def generate_nda_pdf(candidate_name: str, designation: str) -> Path:
    """Generate Employee Confidentiality & Non-Disclosure Agreement."""
    filename = f"NDA_{candidate_name.replace(' ', '_')}.pdf"
    file_path = GENERATED_DOCS_DIR / filename

    doc = SimpleDocTemplate(str(file_path), pagesize=letter, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    styles = getSampleStyleSheet()
    story = []

    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1e3a8a'), alignment=1)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=colors.HexColor('#334155'))

    story.append(Paragraph("<b>EMPLOYEE CONFIDENTIALITY AND PROPRIETARY INFORMATION AGREEMENT</b>", h1_style))
    story.append(Spacer(1, 15))

    p = (
        f"This Confidentiality Agreement is entered into between <b>HR Nexus Enterprises Inc.</b> "
        f"and <b>{candidate_name}</b> (appointed as <b>{designation}</b>).<br/><br/>"
        "1. <b>Confidential Information:</b> Employee acknowledges that during employment they may access sensitive "
        "proprietary technology, source codes, business plans, customer data, and AI architectures.<br/><br/>"
        "2. <b>Non-Disclosure:</b> Employee agrees never to disclose, publish, or transfer any proprietary materials to third parties "
        "without prior written executive authorization.<br/><br/>"
        "3. <b>Intellectual Property Assignment:</b> All software, designs, algorithms, workflows, and inventions conceived during "
        "employment belong solely and exclusively to HR Nexus Enterprises Inc.<br/><br/>"
        "4. <b>Term:</b> Obligations under this agreement continue indefinitely following termination of employment."
    )
    story.append(Paragraph(p, body_style))
    story.append(Spacer(1, 35))

    sig_data = [
        [
            Paragraph("<b>Employer:</b><br/>HR Nexus Enterprises Inc.<br/><br/>By: ___________________________<br/>HR Executive", body_style),
            Paragraph(f"<b>Employee:</b><br/>{candidate_name}<br/><br/>Signature: ___________________________<br/>Date: ________________________", body_style)
        ]
    ]
    t = Table(sig_data, colWidths=[260, 260])
    story.append(t)

    doc.build(story)
    return file_path

