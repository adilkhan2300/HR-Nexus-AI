"""
HR Nexus AI - View 10: Offer Management & Document Generation Hub
"""
import io
import random
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.connection import get_db
from config import DEPARTMENTS, EMPLOYMENT_TYPES
from services.doc_generator import generate_offer_letter_pdf, generate_offer_letter_docx, generate_nda_pdf

def render(user_role: str = "HR Manager"):
    st.markdown("### 📝 Offer Management & Document Generation Hub")
    st.markdown("Generate legally compliant offer letters, appointment agreements, NDAs, and onboarding packets with mandatory HR sign-off.")

    tab_list, tab_create, tab_nda = st.tabs(["Active Offers", "➕ Draft New Offer", "🛡️ Generate NDA & Agreements"])

    # Fetch candidates eligible for offer (Selected / Interview Completed)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id as candidate_id, c.full_name, c.email, a.id as application_id,
                   a.requisition_id, jr.title as job_title, jr.department, jr.min_salary, jr.max_salary
            FROM candidates c
            JOIN applications a ON c.id = a.candidate_id
            JOIN job_requisitions jr ON a.requisition_id = jr.id
            WHERE a.stage IN ('Selected', 'Interview Completed', 'Shortlisted', 'Applied');
        """)
        eligible_cands = [dict(r) for r in cursor.fetchall()]

    # TAB 1: LIST OFFERS
    with tab_list:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.offer_code, c.full_name, o.designation, o.department,
                       o.annual_ctc, o.joining_date, o.offer_status, o.hr_approved_by, o.candidate_id
                FROM offers o
                JOIN candidates c ON o.candidate_id = c.id
                ORDER BY o.id DESC;
            """)
            offers = [dict(r) for r in cursor.fetchall()]

        if offers:
            df_off = pd.DataFrame(offers)
            st.dataframe(df_off[['offer_code', 'full_name', 'designation', 'department', 'annual_ctc', 'joining_date', 'offer_status', 'hr_approved_by']], use_container_width=True, hide_index=True)

            # Document Download & Approval controls
            st.markdown("##### 📄 Export Official Documents")
            sel_off_code = st.selectbox("Select Offer Code:", [o['offer_code'] for o in offers])
            sel_off = next(o for o in offers if o['offer_code'] == sel_off_code)

            c_pdf, c_docx, c_appr = st.columns(3)
            with c_pdf:
                # Generate PDF
                pdf_path = generate_offer_letter_pdf({
                    "offer_code": sel_off['offer_code'],
                    "candidate_name": sel_off['full_name'],
                    "candidate_email": "candidate@example.com",
                    "designation": sel_off['designation'],
                    "department": sel_off['department'],
                    "reporting_manager": "Sarah Jenkins",
                    "joining_date": sel_off['joining_date'],
                    "annual_ctc": sel_off['annual_ctc'],
                    "currency": "USD",
                    "work_location": "Hybrid / Austin, TX",
                    "employment_type": "Full-Time"
                })
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="📥 Download Offer PDF",
                    data=pdf_bytes,
                    file_name=pdf_path.name,
                    mime="application/pdf"
                )

            with c_docx:
                docx_path = generate_offer_letter_docx({
                    "offer_code": sel_off['offer_code'],
                    "candidate_name": sel_off['full_name'],
                    "candidate_email": "candidate@example.com",
                    "designation": sel_off['designation'],
                    "department": sel_off['department'],
                    "reporting_manager": "Sarah Jenkins",
                    "joining_date": sel_off['joining_date'],
                    "annual_ctc": sel_off['annual_ctc'],
                    "currency": "USD",
                    "work_location": "Hybrid / Austin, TX",
                    "employment_type": "Full-Time"
                })
                with open(docx_path, "rb") as f:
                    docx_bytes = f.read()

                st.download_button(
                    label="📥 Download Offer Word (.docx)",
                    data=docx_bytes,
                    file_name=docx_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            with c_appr:
                if sel_off['offer_status'] == 'Draft' and user_role in ['Admin', 'HR Manager']:
                    if st.button("✅ Sign & Release Offer"):
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE offers SET offer_status = 'Released', hr_approved_by = ?, approved_at = CURRENT_TIMESTAMP WHERE id = ?;", (user_role, sel_off['id']))
                            cursor.execute("UPDATE applications SET stage = 'Offer Released' WHERE candidate_id = ?;", (sel_off['candidate_id'],))
                        st.success(f"Offer {sel_off['offer_code']} approved and marked Released!")
                        st.rerun()
                elif sel_off['offer_status'] == 'Released':
                    if st.button("🎉 Candidate Accepted Offer"):
                        with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE offers SET offer_status = 'Accepted' WHERE id = ?;", (sel_off['id'],))
                            cursor.execute("UPDATE applications SET stage = 'Offer Accepted' WHERE candidate_id = ?;", (sel_off['candidate_id'],))
                        st.success("Candidate marked Accepted! Ready for Onboarding initiation.")
                        st.rerun()
        else:
            st.info("No offers drafted yet.")

    # TAB 2: DRAFT NEW OFFER
    with tab_create:
        st.markdown("##### ✍️ Create Formal Offer Proposal")
        if eligible_cands:
            cand_map = {f"{c['full_name']} ({c['job_title']})": c for c in eligible_cands}
            chosen_label = st.selectbox("Select Candidate for Offer:", list(cand_map.keys()))
            chosen_c = cand_map[chosen_label]

            col1, col2 = st.columns(2)
            with col1:
                off_desig = st.text_input("Designation *", value=chosen_c['job_title'])
                off_dept = st.selectbox("Department *", DEPARTMENTS, index=DEPARTMENTS.index(chosen_c['department']) if chosen_c['department'] in DEPARTMENTS else 0)
                off_manager = st.text_input("Reporting Manager *", value="David Chen")
                off_jdate = st.date_input("Proposed Joining Date *", value=datetime.now() + timedelta(days=21))

            with col2:
                off_ctc = st.number_input("Annual Base Compensation ($) *", min_value=30000, max_value=600000, value=int(chosen_c.get('max_salary') or 115000), step=5000)
                off_type = st.selectbox("Employment Type *", EMPLOYMENT_TYPES)
                off_loc = st.text_input("Work Location *", value="Austin, TX (Hybrid)")
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD", "INR"], index=0)

            terms = st.text_area(
                "Terms and Conditions",
                value="Standard 90-day probationary period. Health, dental, vision insurance coverage effective day one. 20 days paid annual leave."
            )

            if st.button("Draft Offer Letter & Submit for HR Sign-off", type="primary"):
                off_code = f"OFF-2026-{random.randint(100, 999)}"
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO offers (
                            offer_code, application_id, candidate_id, requisition_id,
                            designation, department, reporting_manager, joining_date,
                            annual_ctc, currency, work_location, employment_type,
                            terms_and_conditions, offer_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Draft');
                    """, (
                        off_code, chosen_c['application_id'], chosen_c['candidate_id'],
                        chosen_c['requisition_id'], off_desig, off_dept, off_manager,
                        str(off_jdate), off_ctc, currency, off_loc, off_type, terms
                    ))
                    cursor.execute("""
                        INSERT INTO audit_logs (user_action, module, performed_by, details)
                        VALUES (?, ?, ?, ?);
                    """, ("OFFER_DRAFTED", "Offers", user_role, f"Drafted offer {off_code} for {chosen_c['full_name']}"))
                st.success(f"Offer {off_code} drafted successfully! It is queued for HR signature.")
                st.rerun()
        else:
            st.info("No candidates currently eligible for offer generation.")

    # TAB 3: GENERATE NDA & AGREEMENTS
    with tab_nda:
        st.markdown("##### 🛡️ Non-Disclosure & Confidentiality Agreement")
        nda_name = st.text_input("Employee / Candidate Name:", value="Alex Rivera")
        nda_desig = st.text_input("Designation:", value="Senior Python Developer")

        if st.button("Generate & Download PDF NDA"):
            nda_path = generate_nda_pdf(nda_name, nda_desig)
            with open(nda_path, "rb") as f:
                bytes_nda = f.read()
            st.download_button(
                label="📥 Download Signed NDA PDF",
                data=bytes_nda,
                file_name=nda_path.name,
                mime="application/pdf"
            )

