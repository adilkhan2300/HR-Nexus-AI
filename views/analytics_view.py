"""
HR Nexus AI - View 14: HR Analytics & Performance Reporting
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.connection import get_db
from components.ui_helpers import render_metric_card

def render(user_role: str = "HR Manager"):
    st.markdown("### 📈 HR Analytics & Performance Dashboard")
    st.markdown("Dynamic operational metrics, talent funnel velocity, source-of-hire distribution, and onboarding SLA tracking calculated from live database records.")

    with get_db() as conn:
        cursor = conn.cursor()

        # Dynamic KPIs
        cursor.execute("SELECT COUNT(*) as cnt FROM job_requisitions;")
        total_openings = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM applications;")
        total_apps = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM screening_results;")
        total_screened = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM applications WHERE stage = 'Shortlisted';")
        total_shortlisted = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM interviews WHERE status = 'Completed';")
        interviews_conducted = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM offers WHERE offer_status IN ('Released', 'Accepted');")
        offers_released = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM offers WHERE offer_status = 'Accepted';")
        offers_accepted = cursor.fetchone()["cnt"]

        conversion_rate = round((offers_accepted / total_apps * 100), 1) if total_apps > 0 else 0.0

        # Onboarding KPIs
        cursor.execute("SELECT COUNT(*) as cnt, AVG(onboarding_progress) as avg_prog FROM employees;")
        emp_stats = cursor.fetchone()
        total_employees = emp_stats["cnt"]
        avg_onboarding = round(emp_stats["avg_prog"] or 0.0, 1)

        cursor.execute("SELECT COUNT(*) as cnt FROM employee_documents WHERE status IN ('Pending', 'Submitted', 'Under Verification');")
        pending_docs = cursor.fetchone()["cnt"]

        cursor.execute("SELECT COUNT(*) as cnt FROM onboarding_tasks WHERE status = 'Pending';")
        pending_tasks = cursor.fetchone()["cnt"]

    # Render Metric Cards (2 rows)
    st.markdown("#### 🎯 Recruitment Conversion & Funnel KPIs")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Total Applications", str(total_apps), "Across all pipelines", "#2563eb")
    with c2:
        render_metric_card("Screened by AI", str(total_screened), "100% compliant", "#0284c7")
    with c3:
        render_metric_card("Interviews Conducted", str(interviews_conducted), "Multi-round panel", "#7c3aed")
    with c4:
        render_metric_card("Funnel Conversion Rate", f"{conversion_rate}%", "Application-to-Offer", "#10b981")

    st.markdown("#### 🚀 Onboarding SLA & Velocity KPIs")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        render_metric_card("Total Employees", str(total_employees), "Active + Probation", "#0f172a")
    with c6:
        render_metric_card("Avg Onboarding Velocity", f"{avg_onboarding}%", "Across 4 phases", "#6366f1")
    with c7:
        render_metric_card("Pending Document Audits", str(pending_docs), "48-hr SLA clock", "#ef4444")
    with c8:
        render_metric_card("Pending Onboarding Tasks", str(pending_tasks), "Milestones remaining", "#f59e0b")

    st.markdown("---")

    # Plotly Visualizations Section
    col_chart_a, col_chart_b = st.columns(2)

    with col_chart_a:
        st.markdown("##### 📌 Candidate Sourcing Channel Distribution")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT source, COUNT(*) as count FROM applications GROUP BY source;")
            sources = [dict(r) for r in cursor.fetchall()]

        if sources:
            df_src = pd.DataFrame(sources)
            fig_src = px.bar(
                df_src, x='source', y='count',
                color='count', color_continuous_scale='Blues',
                labels={'source': 'Channel', 'count': 'Applicants'},
                text='count'
            )
            fig_src.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_src, use_container_width=True)

    with col_chart_b:
        st.markdown("##### 📊 12-Stage Candidate Funnel")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT stage, COUNT(*) as count FROM applications GROUP BY stage ORDER BY count DESC;")
            stages = [dict(r) for r in cursor.fetchall()]

        if stages:
            df_stg = pd.DataFrame(stages)
            fig_stg = px.pie(df_stg, names='stage', values='count', hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism)
            fig_stg.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_stg, use_container_width=True)

    col_chart_c, col_chart_d = st.columns(2)

    with col_chart_c:
        st.markdown("##### 🏢 Department-Wise Onboarding Progress (%)")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department, AVG(onboarding_progress) as avg_progress FROM employees GROUP BY department;")
            dept_prog = [dict(r) for r in cursor.fetchall()]

        if dept_prog:
            df_dept_prog = pd.DataFrame(dept_prog)
            fig_dept = px.bar(
                df_dept_prog, x='department', y='avg_progress',
                color='avg_progress', color_continuous_scale='Teal',
                labels={'department': 'Department', 'avg_progress': 'Avg Progress (%)'},
                range_y=[0, 100], text='avg_progress'
            )
            fig_dept.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_dept.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_dept, use_container_width=True)

    with col_chart_d:
        st.markdown("##### 📂 Document Verification Status Breakdown")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) as count FROM employee_documents GROUP BY status;")
            doc_stats = [dict(r) for r in cursor.fetchall()]

        if doc_stats:
            df_doc_stats = pd.DataFrame(doc_stats)
            fig_docs = px.pie(df_doc_stats, names='status', values='count', color_discrete_sequence=px.colors.qualitative.Safe)
            fig_docs.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_docs, use_container_width=True)

