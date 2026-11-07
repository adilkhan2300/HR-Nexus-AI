"""
Generate sample PDF and DOCX resume files for testing file upload and parsing.
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from docx import Document
from config import SAMPLE_RESUMES_DIR

def generate_pdf_resume(filename, name, contact, summary, experience, education, skills, certs):
    filepath = SAMPLE_RESUMES_DIR / filename
    doc = SimpleDocTemplate(str(filepath), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor='#1e293b')
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor='#64748b')
    h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=12, leading=15, textColor='#2563eb', spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor='#334155')

    story.append(Paragraph(f"<b>{name}</b>", title_style))
    story.append(Paragraph(contact, sub_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", h2_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>TECHNICAL & SOFT SKILLS</b>", h2_style))
    story.append(Paragraph(skills, body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", h2_style))
    for exp in experience:
        story.append(Paragraph(exp, body_style))
        story.append(Spacer(1, 4))

    story.append(Paragraph("<b>EDUCATION</b>", h2_style))
    story.append(Paragraph(education, body_style))
    story.append(Spacer(1, 8))

    if certs:
        story.append(Paragraph("<b>CERTIFICATIONS & ACHIEVEMENTS</b>", h2_style))
        story.append(Paragraph(certs, body_style))

    doc.build(story)
    return filepath

def generate_docx_resume(filename, name, contact, summary, experience, education, skills, certs):
    filepath = SAMPLE_RESUMES_DIR / filename
    doc = Document()
    doc.add_heading(name, level=1)
    doc.add_paragraph(contact)
    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(summary)
    doc.add_heading("Skills", level=2)
    doc.add_paragraph(skills)
    doc.add_heading("Work Experience", level=2)
    for exp in experience:
        doc.add_paragraph(exp)
    doc.add_heading("Education", level=2)
    doc.add_paragraph(education)
    if certs:
        doc.add_heading("Certifications", level=2)
        doc.add_paragraph(certs)
    doc.save(str(filepath))
    return filepath

def generate_all_samples():
    print("Generating sample PDF & DOCX resumes...")
    # 1. Alex Rivera PDF
    generate_pdf_resume(
        "Alex_Rivera_Senior_Python_Developer.pdf",
        "Alex Rivera",
        "Austin, TX | alex.rivera@example.com | +1 555-0101 | LinkedIn: /in/alexrivera-tech",
        "Senior Software Engineer with 5.5 years of proven experience building resilient microservices using Python, FastAPI, Django, Docker, and PostgreSQL. Reduced latency by 42% on high-throughput cloud platforms.",
        [
            "<b>Senior Software Engineer | Apex Cloud Inc. (2022 - Present)</b><br/>- Architected and deployed 8 microservices using FastAPI, Redis caching, and PostgreSQL.<br/>- Designed CI/CD deployment pipelines on Docker and Kubernetes with automated unit testing.",
            "<b>Software Engineer | NovaTech Solutions (2019 - 2022)</b><br/>- Developed scalable backend REST APIs using Django and PostgreSQL.<br/>- Optimized database queries, reducing average execution time from 450ms to 85ms."
        ],
        "B.S. in Computer Science - University of Texas at Austin (2015 - 2019, GPA: 3.8/4.0)",
        "<b>Technical:</b> Python, FastAPI, Django, PostgreSQL, Docker, Redis, REST APIs, Microservices, Git, Kubernetes, Unit Testing.<br/><b>Soft:</b> Agile leadership, Mentoring, Cross-functional collaboration.",
        "AWS Certified Developer Associate (2023) | Certified Scrum Master (CSM)"
    )

    # 2. Sophia Lin PDF
    generate_pdf_resume(
        "Sophia_Lin_Data_Scientist.pdf",
        "Sophia Lin",
        "San Francisco, CA | sophia.lin@example.com | +1 555-0104 | GitHub: /sophialin-ai",
        "Data Scientist with 4.5 years of industry experience fine-tuning LLMs, building NLP pipelines, and deploying predictive machine learning models in production.",
        [
            "<b>Data Scientist | Insight Analytics (2022 - Present)</b><br/>- Fine-tuned transformer models (Llama, BERT) using PyTorch for enterprise NLP.<br/>- Built real-time inference endpoints deployed on AWS ECS with Docker.",
            "<b>Junior Data Scientist | DataCorp (2020 - 2022)</b><br/>- Engineered features and trained scikit-learn models for customer retention."
        ],
        "M.S. in Data Science - UC Berkeley (2018 - 2020) | B.S. in Statistics - UCLA (2014 - 2018)",
        "<b>Technical:</b> Python, PyTorch, Scikit-learn, LLMs, NLP, Pandas, NumPy, SQL, Feature Engineering, Docker, MLOps.<br/><b>Soft:</b> Scientific curiosity, Data storytelling, Stakeholder communication.",
        "TensorFlow Developer Certificate | Published paper in NeurIPS Workshop 2022"
    )

    # 3. Aisha Khan DOCX
    generate_docx_resume(
        "Aisha_Khan_HR_Executive.docx",
        "Aisha Khan",
        "New York, NY | aisha.khan@example.com | +1 555-0106",
        "Results-driven People Operations Specialist with 3.5 years of experience overseeing full recruitment lifecycles, structured employee onboarding, and HR compliance.",
        [
            "HR Specialist | Vanguard People Co. (2022 - Present)\n- Managed end-to-end recruitment for 60+ technical and business roles.\n- Implemented digital onboarding workflows reducing new-hire time-to-productivity by 30%.",
            "HR Associate | TalentBridge (2021 - 2022)\n- Managed candidate database in BambooHR and facilitated new-hire orientation sessions."
        ],
        "B.A. in Human Resources Management - New York University (2017 - 2021)",
        "End-to-end recruitment, HRMS, Onboarding workflows, Talent sourcing, Statutory compliance, Excel, Candidate experience",
        "SHRM-CP (Society for Human Resource Management Certified Professional)"
    )

    # 4. Emily Watson DOCX
    generate_docx_resume(
        "Emily_Watson_Business_Analyst.docx",
        "Emily Watson",
        "Denver, CO | emily.watson@example.com | +1 555-0108",
        "Lead Business Analyst with 7 years of enterprise consulting experience translating business strategies into technical blueprints, BRDs, and user stories.",
        [
            "Senior Business Consultant | KPMG Advisory (2021 - Present)\n- Led discovery workshops with executive sponsors for multi-million dollar cloud transformations.\n- Authored BPMN process models and prioritized JIRA backlogs for Agile squads.",
            "Business Analyst | Accenture (2017 - 2021)\n- Authored detailed functional specifications and conducted gap analysis."
        ],
        "B.S. in Economics & Business - Colorado State University (2013 - 2017)",
        "Requirements Gathering, BRD/FRD Drafting, SQL, Process Mapping, BPMN, JIRA, Agile/Scrum, Tableau",
        "CBAP (Certified Business Analysis Professional) | PMI-PBA"
    )

    print("Sample resumes generated in sample_resumes/ directory.")

if __name__ == "__main__":
    generate_all_samples()

