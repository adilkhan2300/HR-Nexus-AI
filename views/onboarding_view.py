"""
HR Nexus AI - View 11: Employee Onboarding Agent
"""
import streamlit as st
import pandas as pd
from agents.onboarding_agent import OnboardingAgent
from database.connection import get_db
from config import ONBOARDING_PHASES, DOCUMENT_STATUSES, TASK_STATUSES

def render(user_role: str = "HR Manager"):
    st.markdown("### 🚀 Employee Onboarding Agent")
    st.markdown("Autonomous onboarding coordination across 4 structured phases: Pre-Joining, Day 1, First Week, and First 30 Days with document SLA compliance.")

    agent = OnboardingAgent()

    tab_overview, tab_tasks, tab_docs, tab_initiate = st.tabs([
        "📋 Active Onboarding Profiles", "✅ 4-Phase Task Manager", "📂 Document Verification Hub", "⚡ Initiate New Onboarding"
    ])

    # Fetch employees in onboarding
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY id DESC;")
        employees = [dict(r) for r in cursor.fetchall()]

    # TAB 1: ACTIVE ONBOARDING PROFILES
    with tab_overview:
        st.markdown("##### 👥 Onboarding Status Tracker")
        if employees:
            for emp in employees:
                with st.expander(f"👤 {emp['full_name']} ({emp['employee_code']}) - {emp['designation']} | {emp['department']} - Progress: {emp['onboarding_progress']}%"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Email:** {emp['email']}")
                        st.write(f"**Joining Date:** {emp['joining_date']}")
                        st.write(f"**Location:** {emp['work_location']}")
                    with c2:
                        st.write(f"**Reporting Manager:** {emp['reporting_manager']}")
                        st.write(f"**Status:** `{emp['employment_status']}`")
                        st.write(f"**Docs Status:** `{emp['doc_verification_status']}`")
                    with c3:
                        st.progress(emp['onboarding_progress'] / 100.0)
                        st.write(f"**Progress:** {emp['onboarding_progress']}% Completed")

                    # Quick summary of tasks
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT phase, task_title, status, due_date FROM onboarding_tasks WHERE employee_id = ?;", (emp['id'],))
                        tasks = cursor.fetchall()
                    if tasks:
                        st.dataframe(pd.DataFrame([dict(t) for t in tasks]), use_container_width=True, hide_index=True)
        else:
            st.info("No active employee onboarding profiles.")

    # TAB 2: 4-PHASE TASK MANAGER
    with tab_tasks:
        st.markdown("##### 📋 Manage Onboarding Deliverables by Phase")
        if employees:
            emp_map = {f"{e['full_name']} ({e['employee_code']})": e['id'] for e in employees}
            sel_emp_label = st.selectbox("Select Employee:", list(emp_map.keys()), key="task_emp_sel")
            sel_emp_id = emp_map[sel_emp_label]

            sel_phase = st.selectbox("Filter by Onboarding Phase:", ["All Phases"] + ONBOARDING_PHASES)

            with get_db() as conn:
                cursor = conn.cursor()
                query = "SELECT id, phase, task_title, task_description, assigned_to, due_date, status, completed_by FROM onboarding_tasks WHERE employee_id = ?"
                params = [sel_emp_id]
                if sel_phase != "All Phases":
                    query += " AND phase = ?"
                    params.append(sel_phase)
                query += " ORDER BY id ASC;"
                cursor.execute(query, params)
                emp_tasks = [dict(r) for r in cursor.fetchall()]

            if emp_tasks:
                df_tasks = pd.DataFrame(emp_tasks)
                st.dataframe(df_tasks[['phase', 'task_title', 'assigned_to', 'due_date', 'status', 'completed_by']], use_container_width=True, hide_index=True)

                st.markdown("##### ⚡ Update Task Status")
                col_t1, col_t2, col_t3 = st.columns([2, 1.5, 1])
                with col_t1:
                    t_map = {f"{t['task_title']} ({t['phase']})": t['id'] for t in emp_tasks}
                    sel_t_label = st.selectbox("Select Task to Update:", list(t_map.keys()))
                    sel_t_id = t_map[sel_t_label]
                with col_t2:
                    new_task_status = st.selectbox("New Status:", TASK_STATUSES)
                with col_t3:
                    st.write("")
                    st.write("")
                    if st.button("Save Task Status"):
                        agent.update_task_status(sel_t_id, new_task_status, completed_by=user_role)
                        st.success("Task updated and employee onboarding progress recalculated!")
                        st.rerun()
            else:
                st.info("No tasks found for this phase.")

    # TAB 3: DOCUMENT VERIFICATION HUB
    with tab_docs:
        st.markdown("##### 📂 Statutory & Pre-Joining Document Verification (48-hr SLA)")
        if employees:
            emp_map_doc = {f"{e['full_name']} ({e['employee_code']})": e['id'] for e in employees}
            sel_doc_emp = st.selectbox("Select Employee for Document Audit:", list(emp_map_doc.keys()), key="doc_emp_sel")
            sel_doc_emp_id = emp_map_doc[sel_doc_emp]

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employee_documents WHERE employee_id = ?;", (sel_doc_emp_id,))
                docs = [dict(r) for r in cursor.fetchall()]

            if docs:
                df_docs = pd.DataFrame(docs)
                st.dataframe(df_docs[['document_type', 'document_name', 'status', 'verification_notes', 'verified_by', 'verified_at']], use_container_width=True, hide_index=True)

                st.markdown("##### 🛡️ Verify or Reject Document (Human Review Gate)")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    doc_select_map = {f"{d['document_type']} - Status: {d['status']}": d['id'] for d in docs}
                    target_doc_label = st.selectbox("Select Document:", list(doc_select_map.keys()))
                    target_doc_id = doc_select_map[target_doc_label]
                    ver_status = st.selectbox("Audit Decision:", DOCUMENT_STATUSES, index=3)
                with col_d2:
                    ver_notes = st.text_input("Verification Audit Notes:", value="Document verified against official records. Clear and legible.")

                if st.button("Confirm Document Verification"):
                    agent.update_document_status(target_doc_id, ver_status, ver_notes, verified_by=user_role)
                    st.success("Document status updated and audit logged!")
                    st.rerun()
            else:
                st.info("No documents uploaded for this employee yet.")

    # TAB 4: INITIATE NEW ONBOARDING
    with tab_initiate:
        st.markdown("##### ⚡ Handoff Accepted Offer to Autonomous Onboarding Engine")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id as offer_id, o.candidate_id, c.full_name, o.designation, o.department
                FROM offers o
                JOIN candidates c ON o.candidate_id = c.id
                WHERE o.offer_status = 'Accepted'
                  AND c.id NOT IN (SELECT c2.id FROM candidates c2 JOIN employees e ON c2.email = e.email);
            """)
            accepted_candidates = [dict(r) for r in cursor.fetchall()]

        if accepted_candidates:
            st.write(f"Found **{len(accepted_candidates)}** candidates with accepted offers ready for onboarding:")
            for ac in accepted_candidates:
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**{ac['full_name']}** – Role: {ac['designation']} ({ac['department']})")
                with c2:
                    if st.button(f"🚀 Start Onboarding for {ac['full_name']}", key=f"init_{ac['offer_id']}"):
                        res = agent.initiate_onboarding(ac['candidate_id'], ac['offer_id'], approved_by=user_role)
                        if res.get("success"):
                            st.success(f"🎉 Onboarding successfully initialized for {ac['full_name']}! Employee ID: {res['employee_code']}.")
                            st.rerun()
                        else:
                            st.error(f"Error: {res.get('error')}")
        else:
            st.success("✅ All accepted candidates have already been enrolled into the onboarding system.")

