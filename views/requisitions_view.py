"""
HR Nexus AI - View 3: Manpower Planning & Job Requisition Management
"""
import random
import streamlit as st
import pandas as pd
from database.connection import get_db
from config import DEPARTMENTS, EMPLOYMENT_TYPES, PRIORITIES
from agents.base_agent import BaseAIAgent

def render(user_role: str = "HR Manager"):
    st.markdown("### 📋 Manpower Planning & Job Requisitions")
    st.markdown("Create, review, and track departmental staffing requisitions with automated AI skill recommendations and approval workflows.")

    tab_list, tab_create, tab_ai = st.tabs(["Active Requisitions", "➕ New Job Requisition", "🤖 AI Requisition Assistant"])

    # TAB 1: LIST REQUISITIONS
    with tab_list:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, requisition_code, title, department, employment_type, vacancies,
                       experience_required, min_salary, max_salary, hiring_manager,
                       priority, approval_status, created_at
                FROM job_requisitions
                ORDER BY id DESC;
            """)
            reqs = [dict(r) for r in cursor.fetchall()]

        if reqs:
            df = pd.DataFrame(reqs)
            st.dataframe(
                df[['requisition_code', 'title', 'department', 'vacancies', 'priority', 'approval_status', 'hiring_manager']],
                use_container_width=True,
                hide_index=True
            )

            # Details / Approval Action
            st.markdown("##### 🔍 Inspect or Approve Requisition")
            selected_code = st.selectbox("Select Requisition Code to Inspect:", [r['requisition_code'] for r in reqs])
            sel_req = next((r for r in reqs if r['requisition_code'] == selected_code), None)

            if sel_req:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write(f"**Job Title:** {sel_req['title']}")
                    st.write(f"**Department:** {sel_req['department']}")
                    st.write(f"**Employment Type:** {sel_req['employment_type']}")
                with c2:
                    st.write(f"**Experience:** {sel_req['experience_required']}")
                    st.write(f"**Salary:** ${sel_req['min_salary']:,.0f} - ${sel_req['max_salary']:,.0f}")
                    st.write(f"**Hiring Manager:** {sel_req['hiring_manager']}")
                with c3:
                    st.write(f"**Vacancies:** {sel_req['vacancies']}")
                    st.write(f"**Priority:** `{sel_req['priority']}`")
                    st.write(f"**Status:** `{sel_req['approval_status']}`")

                # Action Buttons
                if user_role in ["Admin", "HR Manager"]:
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button("✅ Approve Requisition", key=f"app_{sel_req['id']}"):
                            with get_db() as conn:
                                conn.cursor().execute("UPDATE job_requisitions SET approval_status = 'Approved', approved_by = ? WHERE id = ?;", (user_role, sel_req['id']))
                                conn.cursor().execute("INSERT INTO audit_logs (user_action, module, performed_by, details) VALUES (?, ?, ?, ?);",
                                                      ("REQUISITION_APPROVED", "Requisitions", user_role, f"Approved {sel_req['requisition_code']}"))
                            st.success(f"Requisition {sel_req['requisition_code']} has been approved!")
                            st.rerun()
                    with col_btn2:
                        if st.button("❌ Reject Requisition", key=f"rej_{sel_req['id']}"):
                            with get_db() as conn:
                                conn.cursor().execute("UPDATE job_requisitions SET approval_status = 'Rejected' WHERE id = ?;", (sel_req['id'],))
                            st.warning(f"Requisition {sel_req['requisition_code']} marked Rejected.")
                            st.rerun()
        else:
            st.info("No requisitions currently in the database.")

    # TAB 2: CREATE REQUISITION
    with tab_create:
        st.markdown("##### Fill Requisition Parameters")
        with st.form("new_req_form"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Job Title *", placeholder="e.g. Senior Backend Engineer")
                dept = st.selectbox("Department *", DEPARTMENTS)
                emp_type = st.selectbox("Employment Type *", EMPLOYMENT_TYPES)
                vacancies = st.number_input("Vacancies *", min_value=1, max_value=50, value=1)
                exp = st.text_input("Experience Required *", value="3-5 Years")
            with c2:
                hiring_manager = st.text_input("Hiring Manager *", value="Sarah Jenkins")
                priority = st.selectbox("Hiring Priority", PRIORITIES, index=1)
                min_sal = st.number_input("Minimum Salary ($)", min_value=30000, max_value=500000, value=85000, step=5000)
                max_sal = st.number_input("Maximum Salary ($)", min_value=30000, max_value=500000, value=120000, step=5000)

            quals = st.text_area("Required Qualifications", value="Bachelor's in Computer Science, Engineering or related technical field.")
            tech_skills = st.text_area("Required Technical Skills", value="Python, FastAPI, PostgreSQL, Docker, Redis, REST APIs")
            soft_skills = st.text_area("Required Soft Skills", value="Problem solving, Proactive communication, Team leadership")
            desc = st.text_area("Brief Job Description / Scope of Work", value="Responsible for building highly available backend services and scalable data pipelines.")

            submitted = st.form_submit_button("Submit Requisition for Approval")
            if submitted:
                if not title.strip():
                    st.error("Please enter a valid Job Title.")
                else:
                    req_code = f"REQ-2026-{random.randint(100, 999)}"
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO job_requisitions (
                                requisition_code, title, department, employment_type, vacancies,
                                experience_required, min_salary, max_salary, salary_currency, hiring_manager,
                                priority, qualifications, technical_skills, soft_skills, job_description,
                                approval_status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'USD', ?, ?, ?, ?, ?, ?, 'Pending');
                        """, (
                            req_code, title, dept, emp_type, vacancies,
                            exp, min_sal, max_sal, hiring_manager,
                            priority, quals, tech_skills, soft_skills, desc
                        ))
                        cursor.execute("""
                            INSERT INTO audit_logs (user_action, module, performed_by, details)
                            VALUES (?, ?, ?, ?);
                        """, ("REQUISITION_CREATED", "Requisitions", user_role, f"Created {req_code} for {title}"))
                    st.success(f"Job Requisition {req_code} created successfully and queued for approval!")
                    st.rerun()

    # TAB 3: AI REQUISITION ASSISTANT
    with tab_ai:
        st.markdown("##### 💡 AI Skill Recommender & Requirements Analyzer")
        ai_title = st.text_input("Enter Target Role for AI Recommendations:", "Cloud DevOps Engineer")
        if st.button("Generate AI Role Insights"):
            agent = BaseAIAgent()
            prompt = f"For the role of '{ai_title}', recommend: 1. Core Technical Skills, 2. Essential Soft Skills, 3. Standard Qualifications, 4. Missing Common Requirements to watch for, 5. Top Hiring Channels."
            with st.spinner("AI analyzing industry talent benchmarks..."):
                insights = agent.generate_text("You are an expert talent acquisition consultant.", prompt)
            st.markdown(insights)

