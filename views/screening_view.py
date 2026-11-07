"""
HR Nexus AI - View 6: AI Resume Screening & Parsing Agent
"""
import streamlit as st
import pandas as pd
from database.connection import get_db
from agents.screening_agent import ScreeningAgent
from services.resume_parser import extract_text_from_file, parse_resume_heuristics

def render(user_role: str = "HR Manager"):
    st.markdown("### 🔍 AI Resume Screening & Parsing Agent")
    st.markdown("Automated candidate qualification evaluation with transparent scoring criteria, explainable rationale, and zero protected-characteristic bias.")

    st.warning("""
    ⚖️ **Responsible AI & Non-Discrimination Notice:**
    Evaluation criteria strictly evaluate job-relevant technical capabilities, experience duration, and educational credentials. Protected characteristics (gender, age, ethnicity, religion, marital status, or photographs) are excluded from scoring models. Final hiring decisions are reserved exclusively for authorized human recruiters.
    """)

    screening_agent = ScreeningAgent()

    # Select Requisition to Screen Against
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, requisition_code, title, experience_required, technical_skills, qualifications FROM job_requisitions WHERE approval_status = 'Approved';")
        req_rows = cursor.fetchall()

    req_map = {f"{r['requisition_code']} - {r['title']}": dict(r) for r in req_rows}
    sel_req_title = st.selectbox("Select Target Job Requisition to Screen Against:", list(req_map.keys()))
    sel_job = req_map[sel_req_title]

    tab_screened, tab_run = st.tabs(["📋 Screening Results Report", "⚡ Execute Batch Screening"])

    # TAB 1: SCREENING RESULTS REPORT
    with tab_screened:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.id as candidate_id, c.full_name, c.highest_education, c.total_experience_years,
                    sr.id as screening_id, sr.skills_match_score, sr.experience_match_score,
                    sr.education_match_score, sr.overall_match_score, sr.matching_skills,
                    sr.missing_skills, sr.verification_flags, sr.recommendation,
                    sr.screening_rationale, sr.human_reviewed, a.stage, a.id as application_id
                FROM screening_results sr
                JOIN applications a ON sr.application_id = a.id
                JOIN candidates c ON sr.candidate_id = c.id
                WHERE sr.requisition_id = ?
                ORDER BY sr.overall_match_score DESC;
            """, (sel_job['id'],))
            results = [dict(r) for r in cursor.fetchall()]

        if results:
            df = pd.DataFrame(results)
            # Display main screening report table as specified in prompt:
            # Candidate Name | Skills Match | Experience Match | Education Match | Overall Match | Missing Requirements | Recommendation
            df_display = df[['full_name', 'skills_match_score', 'experience_match_score', 'education_match_score', 'overall_match_score', 'missing_skills', 'recommendation']].copy()
            df_display.columns = ['Candidate Name', 'Skills Match (%)', 'Exp Match (%)', 'Edu Match (%)', 'Overall Match (%)', 'Missing Requirements', 'AI Recommendation']
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Deep-dive candidate inspector
            st.markdown("##### 🔎 Candidate Explainability & Verification Details")
            c_names = [r['full_name'] for r in results]
            chosen_c_name = st.selectbox("Inspect Explainability Rationale for Candidate:", c_names)
            chosen_res = next(r for r in results if r['full_name'] == chosen_c_name)

            col1, col2 = st.columns([1.2, 1])
            with col1:
                st.markdown(f"**Candidate:** {chosen_res['full_name']} (App ID #{chosen_res['application_id']})")
                st.markdown(f"**Overall Score:** `{chosen_res['overall_match_score']}%` | **Stage:** `{chosen_res['stage']}`")
                st.markdown(f"**Matching Skills:** `{chosen_res['matching_skills']}`")
                st.markdown(f"**Missing Skills:** `{chosen_res['missing_skills']}`")
                st.info(f"**Explainable Rationale:** {chosen_res['screening_rationale']}")
            with col2:
                st.markdown("**Verification Flags:**")
                st.warning(chosen_res['verification_flags'])
                st.markdown(f"**Human Reviewed:** {'✅ Yes' if chosen_res['human_reviewed'] else '⏳ Pending Review'}")

                if st.button("Mark as Human Reviewed & Verified"):
                    with get_db() as conn:
                        conn.cursor().execute("UPDATE screening_results SET human_reviewed = 1, reviewed_by = ? WHERE id = ?;", (user_role, chosen_res['screening_id']))
                        conn.cursor().execute("INSERT INTO audit_logs (user_action, module, performed_by, details) VALUES (?, ?, ?, ?);",
                                              ("SCREENING_VERIFIED", "Screening", user_role, f"Human verified screening for {chosen_res['full_name']}"))
                    st.success("Candidate screening marked as human-reviewed!")
                    st.rerun()
        else:
            st.info(f"No candidates screened for {sel_job['title']} yet. Run batch screening in the next tab!")

    # TAB 2: EXECUTE BATCH SCREENING
    with tab_run:
        st.markdown(f"##### 🚀 Run AI Screening for Applicants of '{sel_job['title']}'")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, a.id as application_id
                FROM candidates c
                JOIN applications a ON c.id = a.candidate_id
                WHERE a.requisition_id = ?;
            """, (sel_job['id'],))
            pending_candidates = [dict(r) for r in cursor.fetchall()]

        st.write(f"Found **{len(pending_candidates)}** candidates linked to this requisition.")

        if st.button("⚡ Start Autonomous AI Screening"):
            prog = st.progress(0)
            screened_now = 0
            for i, cand in enumerate(pending_candidates):
                # Fetch skills for candidate
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT skill_name FROM candidate_skills WHERE candidate_id = ?;", (cand['id'],))
                    skills = [r['skill_name'] for r in cursor.fetchall()]
                    cand['technical_skills'] = skills
                    cand['soft_skills'] = ["Communication", "Problem Solving", "Adaptability"]

                res = screening_agent.screen_candidate(cand, sel_job)
                screening_agent.save_screening_result(cand['application_id'], cand['id'], sel_job['id'], res, reviewed_by=user_role)
                screened_now += 1
                prog.progress((i + 1) / len(pending_candidates))

            st.success(f"Successfully evaluated and scored {screened_now} candidates against '{sel_job['title']}' requirements!")
            st.rerun()

