"""
HR Nexus AI - View 4: AI Job Description Generator & Publishing Hub
"""
import io
import streamlit as st
from docx import Document
from agents.jd_generator_agent import JDGeneratorAgent
from database.connection import get_db
from config import DEPARTMENTS

def render(user_role: str = "HR Manager"):
    st.markdown("### ✨ AI-Powered Job Description Generator")
    st.markdown("Generate comprehensive, high-converting enterprise job descriptions adhering to industry best practices, compliance standards, and STAR interview banks.")

    jd_agent = JDGeneratorAgent()

    # Pre-populate from existing requisition if desired
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, requisition_code, title FROM job_requisitions WHERE approval_status = 'Approved';")
        approved_reqs = cursor.fetchall()

    req_options = {f"{r['requisition_code']} - {r['title']}": r['id'] for r in approved_reqs}
    sel_req_label = st.selectbox("Link to Approved Requisition (Optional):", ["None (Custom Role)"] + list(req_options.keys()))

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        role_title = st.text_input("Job Title", value="Senior Python Developer")
        department = st.selectbox("Department", DEPARTMENTS, index=0)
        experience = st.text_input("Experience Required", value="4-7 Years")
        salary_range = st.text_input("Salary Range", value="$95,000 - $135,000 USD")

    with col_in2:
        qualifications = st.text_area("Required Qualifications", value="Bachelor's or Master's in Computer Science or related STEM field.")
        tech_skills = st.text_area("Technical Skills", value="Python, FastAPI, Django, PostgreSQL, Docker, Redis, REST APIs, Microservices")
        soft_skills = st.text_area("Soft Skills", value="Agile leadership, Technical mentorship, Problem solving, Clear architectural communication")

    responsibilities = st.text_area(
        "Key Responsibilities / Role Scope",
        value="Architect scalable microservices with FastAPI; Optimize SQL query plans; Mentor junior developers; Maintain 99.9% uptime SLA."
    )

    if st.button("🚀 Generate AI Job Description", type="primary"):
        with st.spinner("AI Talent Acquisition Agent drafting comprehensive Job Description..."):
            jd_result = jd_agent.generate_job_description(
                title=role_title,
                department=department,
                experience=experience,
                qualifications=qualifications,
                technical_skills=tech_skills,
                soft_skills=soft_skills,
                responsibilities_input=responsibilities,
                salary_range=salary_range
            )
            st.session_state["generated_jd"] = jd_result

    # Display & Edit Output
    if "generated_jd" in st.session_state:
        jd = st.session_state["generated_jd"]
        st.markdown("---")
        st.markdown(f"#### 📄 Generated Job Description: {jd['title']}")

        # Editable fields
        edited_overview = st.text_area("Job Overview", value=jd['overview'], height=100)
        edited_resp = st.text_area("Key Responsibilities", value=jd['responsibilities'], height=140)
        edited_culture = st.text_area("Company Culture & Expectations", value=jd['company_expectations'], height=100)

        c_q, c_ch = st.columns(2)
        with c_q:
            st.markdown("##### 🎯 Recommended STAR Interview Questions")
            st.info(jd['interview_questions'])
        with c_ch:
            st.markdown("##### 📢 Recommended Sourcing Channels")
            st.info(jd['hiring_channels'])

        # Actions: Save to DB and Download
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("💾 Save to Job Descriptions Repository"):
                req_id = req_options.get(sel_req_label) if sel_req_label != "None (Custom Role)" else None
                save_data = jd.copy()
                save_data['overview'] = edited_overview
                save_data['responsibilities'] = edited_resp
                save_data['company_expectations'] = edited_culture
                jd_agent.save_jd(req_id, save_data)
                st.success("Job Description saved to database repository successfully!")

        with col_act2:
            # Generate downloadable DOCX in-memory
            doc = Document()
            doc.add_heading(f"Job Description: {jd['title']}", level=0)
            doc.add_paragraph(f"Department: {jd['department']} | Experience: {jd['experience_requirements']}")
            doc.add_paragraph(f"Salary: {jd['salary_range']}")
            doc.add_heading("Job Overview", level=2)
            doc.add_paragraph(edited_overview)
            doc.add_heading("Responsibilities", level=2)
            doc.add_paragraph(edited_resp)
            doc.add_heading("Technical & Soft Skills", level=2)
            doc.add_paragraph(f"Technical: {jd['technical_skills']}\nSoft: {jd['soft_skills']}")
            doc.add_heading("Company Expectations & Culture", level=2)
            doc.add_paragraph(edited_culture)

            docx_io = io.BytesIO()
            doc.save(docx_io)
            docx_io.seek(0)

            st.download_button(
                label="📥 Download as Word (.docx)",
                data=docx_io,
                file_name=f"Job_Description_{jd['title'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

