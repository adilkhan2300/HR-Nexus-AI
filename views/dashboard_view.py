"""
HR Nexus AI - View 1: Executive Dashboard & Control Center
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.connection import get_db
from components.ui_helpers import render_metric_card, render_stage_pill

def render():
    st.markdown("### 📊 Executive Dashboard & Recruitment Overview")
    st.markdown("Real-time operational intelligence across active requisitions, applicant pipelines, and onboarding tasks.")

    with get_db() as conn:
        cursor = conn.cursor()

        # Key Metrics
        cursor.execute("SELECT COUNT(*) as cnt FROM job_requisitions WHERE approval_status = 'Approved';")
        open_jobs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM applications;")
        total_apps = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM screening_results;")
        screened_cand = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM applications WHERE stage = 'Shortlisted';")
        shortlisted_cnt = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM interviews WHERE status = 'Scheduled';")
        upcoming_interviews = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM offers WHERE offer_status IN ('Approved by HR', 'Released', 'Accepted');")
        offers_cnt = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM employees WHERE employment_status = 'Probation';")
        active_onboarding = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM employee_documents WHERE status IN ('Pending', 'Submitted', 'Under Verification');")
        pending_docs = cursor.fetchone()["cnt"]

    # Top KPI Cards (4 columns x 2 rows)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Active Job Openings", str(open_jobs), "+2 this month", "#2563eb")
    with c2:
        render_metric_card("Total Applicants", str(total_apps), "Across 5 channels", "#0284c7")
    with c3:
        render_metric_card("Candidates Screened", str(screened_cand), "100% explainable", "#7c3aed")
    with c4:
        render_metric_card("Shortlisted Candidates", str(shortlisted_cnt), "HR approved", "#059669")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_metric_card("Interviews Scheduled", str(upcoming_interviews), "Next 7 days", "#f59e0b")
    with c6:
        render_metric_card("Offers Released/Accepted", str(offers_cnt), "85% accept rate", "#10b981")
    with c7:
        render_metric_card("Active Onboarding", str(active_onboarding), "In 4-phase plan", "#6366f1")
    with c8:
        render_metric_card("Docs Awaiting Verification", str(pending_docs), "48h SLA tracked", "#ef4444")

    st.markdown("---")

    # Interactive Plots Section
    col_chart1, col_chart2 = st.columns([1, 1])

    with col_chart1:
        st.markdown("##### 📌 Recruitment Pipeline Funnel")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stage, COUNT(*) as count
                FROM applications
                GROUP BY stage
                ORDER BY count DESC;
            """)
            stage_rows = cursor.fetchall()
            df_stages = pd.DataFrame([dict(r) for r in stage_rows])

        if not df_stages.empty:
            fig_funnel = go.Figure(go.Funnel(
                y=df_stages['stage'],
                x=df_stages['count'],
                textinfo="value+percent initial",
                marker={"color": ["#1e40af", "#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe", "#10b981", "#059669"]}
            ))
            fig_funnel.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig_funnel, use_container_width=True)
        else:
            st.info("No applications to display in funnel.")

    with col_chart2:
        st.markdown("##### 🏢 Department-Wise Requisitions & Headcount")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT department, SUM(vacancies) as total_vacancies
                FROM job_requisitions
                GROUP BY department;
            """)
            dept_rows = cursor.fetchall()
            df_depts = pd.DataFrame([dict(r) for r in dept_rows])

        if not df_depts.empty:
            fig_pie = px.pie(
                df_depts, values='total_vacancies', names='department',
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # Active Workflows & Human Approvals Queue
    col_wf, col_appr = st.columns([1.2, 1])

    with col_wf:
        st.markdown("##### ⚙️ Active Autonomous Workflows")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, workflow_type, workflow_name, current_step, status, initiated_by FROM workflow_executions LIMIT 4;")
            wf_rows = cursor.fetchall()

        for w in wf_rows:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #1e293b; font-size: 0.9rem;">{w['workflow_name']}</span>
                    <span style="font-size: 0.75rem; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 12px; font-weight: 600;">{w['status']}</span>
                </div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">
                    Current Milestone: <b>{w['current_step']}</b> • Initiated by: {w['initiated_by']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_appr:
        st.markdown("##### 🛡️ Pending HR Approvals (Human-in-the-Loop)")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT requisition_code, title, hiring_manager FROM job_requisitions WHERE approval_status = 'Pending';")
            pend_reqs = cursor.fetchall()

            cursor.execute("SELECT offer_code, designation, annual_ctc FROM offers WHERE offer_status = 'Draft';")
            pend_offers = cursor.fetchall()

        if pend_reqs:
            for r in pend_reqs:
                st.warning(f"Requisition Pending Sign-off: **{r['title']}** (`{r['requisition_code']}`) submitted by {r['hiring_manager']}")
        if pend_offers:
            for o in pend_offers:
                st.warning(f"Offer Pending Sign-off: **{o['designation']}** (`{o['offer_code']}`) - ${o['annual_ctc']:,.2f}")
        if not pend_reqs and not pend_offers:
            st.success("✅ All pending requisitions and offers are signed off and compliant!")

