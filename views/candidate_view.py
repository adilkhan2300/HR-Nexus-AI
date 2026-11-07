"""
HR Nexus AI - View 5: Candidate Application Management & Interactive Pipeline Kanban
"""
import io
import random
import streamlit as st
import pandas as pd
from database.connection import get_db
from config import PIPELINE_STAGES, STAGE_COLORS
from services.resume_parser import extract_text_from_file, parse_resume_heuristics
from services.whatsapp_service import WhatsAppNotificationService

def render(user_role: str = "HR Manager"):
    st.markdown("### 👥 Candidate Application Management")
    st.markdown("Central applicant tracking system managing candidates across all 12 pipeline stages, interactive progression, resume ingestion, and recruiter activity logs.")

    tab_pipeline, tab_directory, tab_upload, tab_manual = st.tabs([
        "📊 Pipeline Kanban Board", "🗂️ Candidate Directory", "📤 Resume Upload (Single & Bulk)", "➕ Add Candidate Manually"
    ])

    # Fetch all candidates with application info & screening score
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                c.id as candidate_id, c.candidate_code, c.full_name, c.email, c.phone,
                c.location, c.highest_education, c.total_experience_years, c.current_organization,
                c.current_designation, c.expected_salary,
                a.id as application_id, a.stage, a.source, a.applied_date,
                jr.id as requisition_id, jr.title as job_title, jr.requisition_code,
                COALESCE(sr.overall_match_score, 0) as overall_match_score
            FROM candidates c
            JOIN applications a ON c.id = a.candidate_id
            JOIN job_requisitions jr ON a.requisition_id = jr.id
            LEFT JOIN screening_results sr ON a.id = sr.application_id
            ORDER BY c.id DESC;
        """)
        all_candidates = [dict(r) for r in cursor.fetchall()]

    # Helper function to move candidate stage with audit trail & WhatsApp alert
    def move_candidate_stage(app_id: int, cand_name: str, new_stage: str, old_stage: str):
        with get_db() as conn:
            c = conn.cursor()
            c.execute("UPDATE applications SET stage = ? WHERE id = ?;", (new_stage, app_id))
            c.execute(
                "INSERT INTO audit_logs (user_action, module, performed_by, details) VALUES (?, ?, ?, ?);",
                ("STAGE_UPDATED", "Candidate Kanban", user_role, f"Moved {cand_name} (App #{app_id}) from '{old_stage}' to '{new_stage}'")
            )

        # Trigger WhatsApp notification if candidate is shortlisted
        if new_stage == "Shortlisted":
            wa = WhatsAppNotificationService()
            wa.send_shortlist_alert(
                candidate_name=cand_name,
                job_title="Assigned Role",
                phone=st.session_state.get("wa_phone_number")
            )
            st.toast(f"📱 WhatsApp Shortlist Notification dispatched for {cand_name}!", icon="💬")

        st.toast(f"✅ Moved **{cand_name}** to **{new_stage}**!", icon="🚀")
        st.rerun()

    # TAB 1: INTERACTIVE PIPELINE KANBAN BOARD
    with tab_pipeline:
        st.markdown("##### 🚀 12-Stage Candidate Recruitment Pipeline")
        st.caption("Organize, review, and progress applicants across every recruitment milestone. Advance candidates with one click or move them to any target stage.")

        c_filt, c_quick = st.columns([1.5, 2])
        with c_filt:
            job_list = ["All Jobs"] + sorted(list(set([c['job_title'] for c in all_candidates])))
            filter_job = st.selectbox("Filter Pipeline by Job Opening:", job_list)

        filtered_cands = all_candidates if filter_job == "All Jobs" else [c for c in all_candidates if c['job_title'] == filter_job]

        with c_quick:
            with st.expander("⚡ Quick Move Tool (Jump Candidate to Any Stage)"):
                q_col1, q_col2, q_col3 = st.columns([2, 2, 1])
                with q_col1:
                    cand_lookup = {f"{c['full_name']} ({c['job_title']} - {c['stage']})": c for c in filtered_cands}
                    if cand_lookup:
                        sel_q_cand_label = st.selectbox("Select Candidate:", list(cand_lookup.keys()), key="quick_move_sel")
                        sel_q_cand = cand_lookup[sel_q_cand_label]
                    else:
                        sel_q_cand = None
                with q_col2:
                    if sel_q_cand:
                        curr_idx = PIPELINE_STAGES.index(sel_q_cand['stage']) if sel_q_cand['stage'] in PIPELINE_STAGES else 0
                        dest_stage = st.selectbox("Move to Stage:", PIPELINE_STAGES, index=curr_idx, key="quick_dest_stage")
                with q_col3:
                    st.write("")
                    st.write("")
                    if sel_q_cand and st.button("Move Now", key="quick_move_btn"):
                        if dest_stage != sel_q_cand['stage']:
                            move_candidate_stage(sel_q_cand['application_id'], sel_q_cand['full_name'], dest_stage, sel_q_cand['stage'])

        st.markdown("---")

        # Stage Groups: 3 Rows of 4 Columns each covering all 12 stages
        stage_groups = [
            ("Stage 1-4: Sourcing & Initial Evaluation", ["Applied", "Resume Screening", "Shortlisted", "Assessment"]),
            ("Stage 5-8: Interviewing & Selection", ["Interview Scheduled", "Interview Completed", "Selected", "Offer Released"]),
            ("Stage 9-12: Handoff & Archival", ["Offer Accepted", "Hired", "Talent Pool", "Rejected"])
        ]

        for group_label, stages_in_group in stage_groups:
            st.markdown(f"###### 📌 {group_label}")
            cols = st.columns(4)

            for idx, stage_name in enumerate(stages_in_group):
                with cols[idx]:
                    stage_color = STAGE_COLORS.get(stage_name, "#64748b")
                    stage_cands = [c for c in filtered_cands if c['stage'] == stage_name]

                    # Column Header Box (unindented to prevent markdown code-block interpretation)
                    st.markdown(
                        f'<div style="background: #1e293b; border-top: 3px solid {stage_color}; border: 1px solid #334155; border-radius: 8px 8px 0 0; padding: 8px 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.2);">'
                        f'<span style="font-weight: 700; font-size: 0.85rem; color: #f8fafc;">{stage_name}</span>'
                        f'<span style="background: {stage_color}25; color: {stage_color}; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 12px; border: 1px solid {stage_color}50;">{len(stage_cands)}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    # Cards container
                    if not stage_cands:
                        st.markdown(
                            '<div style="border: 1px dashed #334155; border-top: none; padding: 18px 8px; text-align: center; color: #64748b; font-size: 0.78rem; border-radius: 0 0 8px 8px; margin-bottom: 16px; background: rgba(30, 41, 59, 0.4);">'
                            'No candidates in this stage'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        for sc in stage_cands:
                            score_badge = ""
                            if sc.get('overall_match_score') and sc['overall_match_score'] > 0:
                                score_badge = f'<div style="margin-top: 4px;"><span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 0.72rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">★ {sc["overall_match_score"]}% Match</span></div>'

                            # Candidate Card with dark-theme native colors
                            card_html = (
                                f'<div style="background: #1e293b; border: 1px solid #334155; border-top: none; padding: 10px 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.25); margin-bottom: 6px;">'
                                f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
                                f'<span style="font-weight: 800; font-size: 0.9rem; color: #f8fafc;">{sc["full_name"]}</span>'
                                f'<span style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">#{sc["candidate_code"]}</span>'
                                f'</div>'
                                f'<div style="color: #60a5fa; font-size: 0.78rem; font-weight: 600; margin: 3px 0;">{sc["job_title"]}</div>'
                                f'{score_badge}'
                                f'<div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #94a3b8; margin-top: 6px; padding-top: 6px; border-top: 1px solid #334155;">'
                                f'<span><b>Exp:</b> {sc["total_experience_years"]} yrs</span>'
                                f'<span style="color: #34d399; font-weight: 600;">{sc["location"]}</span>'
                                f'</div>'
                                f'</div>'
                            )
                            st.markdown(card_html, unsafe_allow_html=True)

                            # Interactive One-Click Progression Bar for this candidate
                            curr_stage_idx = PIPELINE_STAGES.index(stage_name) if stage_name in PIPELINE_STAGES else 0
                            prev_stage = PIPELINE_STAGES[curr_stage_idx - 1] if curr_stage_idx > 0 else None
                            next_stage = PIPELINE_STAGES[curr_stage_idx + 1] if curr_stage_idx < len(PIPELINE_STAGES) - 1 else None

                            btn_col1, btn_col2 = st.columns([1, 1])
                            with btn_col1:
                                if prev_stage:
                                    if st.button(f"◀ Back", key=f"prev_{sc['application_id']}", help=f"Move back to {prev_stage}", use_container_width=True):
                                        move_candidate_stage(sc['application_id'], sc['full_name'], prev_stage, stage_name)
                            with btn_col2:
                                if next_stage:
                                    if st.button(f"Next ▶", key=f"next_{sc['application_id']}", help=f"Advance to {next_stage}", use_container_width=True):
                                        move_candidate_stage(sc['application_id'], sc['full_name'], next_stage, stage_name)

                        # Bottom spacer for column
                        st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # TAB 2: CANDIDATE DIRECTORY & STAGE UPDATER
    with tab_directory:
        search_query = st.text_input("🔍 Search candidates by name, email, or skill:", "")
        cands_to_show = all_candidates
        if search_query:
            q = search_query.lower()
            cands_to_show = [c for c in cands_to_show if q in c['full_name'].lower() or q in c['email'].lower() or q in c['job_title'].lower()]

        df_show = pd.DataFrame(cands_to_show)
        if not df_show.empty:
            st.dataframe(
                df_show[['candidate_code', 'full_name', 'email', 'job_title', 'total_experience_years', 'highest_education', 'stage', 'location']],
                use_container_width=True,
                hide_index=True
            )

            # Stage update form
            st.markdown("##### ⚡ Update Candidate Stage (Human-in-the-Loop)")
            col_sel, col_new_stage, col_upd_btn = st.columns([1.5, 1.5, 1])
            with col_sel:
                cand_map = {f"{c['full_name']} ({c['job_title']})": c for c in cands_to_show}
                chosen_label = st.selectbox("Select Candidate:", list(cand_map.keys()))
                chosen_cand = cand_map[chosen_label]
            with col_new_stage:
                new_stg = st.selectbox("New Stage:", PIPELINE_STAGES, index=PIPELINE_STAGES.index(chosen_cand['stage']) if chosen_cand['stage'] in PIPELINE_STAGES else 0)
            with col_upd_btn:
                st.write("")
                st.write("")
                if st.button("Update Stage"):
                    with get_db() as conn:
                        conn.cursor().execute("UPDATE applications SET stage = ? WHERE id = ?;", (new_stg, chosen_cand['application_id']))
                        conn.cursor().execute("INSERT INTO audit_logs (user_action, module, performed_by, details) VALUES (?, ?, ?, ?);",
                                              ("STAGE_UPDATED", "Candidate Management", user_role, f"Moved {chosen_cand['full_name']} to {new_stg}"))
                    st.success(f"Candidate {chosen_cand['full_name']} moved to '{new_stg}'!")
                    st.rerun()

    # TAB 3: RESUME UPLOAD (SINGLE & BULK)
    with tab_upload:
        st.markdown("##### 📤 Ingest Resumes in Bulk (PDF or DOCX)")
        st.markdown("Upload multiple candidate resumes. The AI Resume Agent will extract contact info, experience, skills, and map them to open requisitions.")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, requisition_code, title FROM job_requisitions WHERE approval_status = 'Approved';")
            req_rows = cursor.fetchall()
        req_target = {f"{r['requisition_code']} - {r['title']}": r['id'] for r in req_rows}
        target_req_name = st.selectbox("Assign Uploaded Resumes to Requisition:", list(req_target.keys()))
        target_req_id = req_target[target_req_name]

        uploaded_files = st.file_uploader("Choose PDF or DOCX resume files", type=["pdf", "docx", "txt"], accept_multiple_files=True)

        if uploaded_files and st.button(f"Process & Ingest {len(uploaded_files)} Resumes"):
            ingested_count = 0
            for f in uploaded_files:
                raw_text = extract_text_from_file(f, f.name)
                parsed = parse_resume_heuristics(raw_text)

                cand_code = f"CAND-{random.randint(100, 999)}"
                app_code = f"APP-2026-{random.randint(100, 999)}"

                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO candidates (
                            candidate_code, full_name, email, phone, location,
                            highest_education, total_experience_years, current_organization,
                            current_designation, notice_period_days, expected_salary
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        cand_code, parsed['full_name'], parsed['email'], parsed['phone'],
                        parsed['location'], parsed['highest_education'], parsed['total_experience_years'],
                        parsed['current_organization'], parsed['current_designation'],
                        parsed['notice_period_days'], parsed['expected_salary']
                    ))
                    new_cand_id = cursor.lastrowid

                    # Save resume raw text
                    cursor.execute("""
                        INSERT INTO resumes (candidate_id, file_name, file_path, raw_text)
                        VALUES (?, ?, ?, ?);
                    """, (new_cand_id, f.name, f"/uploads/{f.name}", raw_text))

                    # Save skills
                    for skill in parsed['technical_skills']:
                        cursor.execute("INSERT INTO candidate_skills (candidate_id, skill_name, skill_type) VALUES (?, ?, 'Technical');", (new_cand_id, skill))

                    # Create Application record
                    cursor.execute("""
                        INSERT INTO applications (application_code, candidate_id, requisition_id, stage, source)
                        VALUES (?, ?, ?, 'Resume Screening', 'Bulk Upload');
                    """, (app_code, new_cand_id, target_req_id))

                    ingested_count += 1

            st.success(f"🎉 Successfully ingested and parsed {ingested_count} resumes! Candidates assigned to '{target_req_name}'.")
            st.rerun()

    # TAB 4: MANUAL CANDIDATE REGISTRATION
    with tab_manual:
        with st.form("manual_cand_form"):
            c1, c2 = st.columns(2)
            with c1:
                m_name = st.text_input("Full Name *", value="Jordan Miller")
                m_email = st.text_input("Email *", value="jordan.m@example.com")
                m_phone = st.text_input("Phone Number", value="+1 555-0144")
                m_loc = st.text_input("Location", value="Austin, TX")
                m_edu = st.text_input("Highest Education", value="B.S. in Computer Science")
            with c2:
                m_exp = st.number_input("Total Experience (Years)", min_value=0.0, max_value=40.0, value=4.0, step=0.5)
                m_org = st.text_input("Current Organization", value="Apex Systems")
                m_desig = st.text_input("Current Designation", value="Software Engineer")
                m_notice = st.number_input("Notice Period (Days)", min_value=0, max_value=180, value=30)
                m_sal = st.number_input("Expected Salary ($)", min_value=20000, max_value=500000, value=115000)

            m_submit = st.form_submit_button("Add Candidate")
            if m_submit:
                c_code = f"CAND-{random.randint(100, 999)}"
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO candidates (
                            candidate_code, full_name, email, phone, location,
                            highest_education, total_experience_years, current_organization,
                            current_designation, notice_period_days, expected_salary
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (c_code, m_name, m_email, m_phone, m_loc, m_edu, m_exp, m_org, m_desig, m_notice, m_sal))
                st.success(f"Candidate {m_name} added to database!")
                st.rerun()
