"""
HR Nexus AI - Intelligent Recruitment & Employee Onboarding Agent
Main Streamlit Application & Lifecycle Router
"""
import streamlit as st
import os

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title="HR Nexus AI - Autonomous Recruitment & Onboarding Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, ROLES
from components.styles import MAIN_CSS
from components.ui_helpers import render_brand_header
from database.connection import init_db
from database.seed_data import seed_all_data
from agents.base_agent import BaseAIAgent

# Import Views
from views import (
    dashboard_view,
    chat_view,
    requisitions_view,
    jd_generator_view,
    candidate_view,
    screening_view,
    shortlisting_view,
    interview_view,
    communication_view,
    offer_view,
    onboarding_view,
    employee_db_view,
    policy_view,
    analytics_view,
    settings_view
)

# Apply CSS styling
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Auto-seed sample database if not already initialized
seed_all_data()

# Initialize AI Agent instance to determine active provider
ai_agent = BaseAIAgent()
active_provider = ai_agent.get_active_provider()

# SIDEBAR: Profile & Navigation
with st.sidebar:
    st.markdown(f"## ⚡ {APP_NAME}")
    st.caption(f"{APP_SUBTITLE} • v{APP_VERSION}")

    st.markdown("---")
    st.markdown("##### 👤 User Role Simulation")
    selected_role = st.selectbox(
        "Current Active Role:",
        ["HR Manager", "Admin", "Interviewer / Dept Manager"],
        index=0,
        help="Switch user roles to simulate permissions and access controls across modules."
    )

    st.markdown("---")
    st.markdown("##### 🧭 Navigation Hub")

    nav_options = [
        "1. Dashboard",
        "2. AI HR Agent",
        "3. Job Requisitions",
        "4. Job Description Generator",
        "5. Candidate Management",
        "6. Resume Screening",
        "7. Shortlisting",
        "8. Interview Management",
        "9. Communication Center",
        "10. Offer Management",
        "11. Employee Onboarding",
        "12. Employee Database",
        "13. HR Policies & SOPs",
        "14. Analytics & Reports",
        "15. Settings & Audit Logs"
    ]

    selected_view = st.radio(
        "Select Module:",
        nav_options,
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"**AI Engine:** `{active_provider}`")
    st.caption("Human-in-the-Loop AI Governance • Ethical & Non-Discriminatory Screening")

# Render Brand Header
render_brand_header(role_name=selected_role, active_provider=active_provider)

# ROUTE TO VIEW MODULE
try:
    if "1. Dashboard" in selected_view:
        dashboard_view.render()
    elif "2. AI HR Agent" in selected_view:
        chat_view.render(user_role=selected_role)
    elif "3. Job Requisitions" in selected_view:
        requisitions_view.render(user_role=selected_role)
    elif "4. Job Description Generator" in selected_view:
        jd_generator_view.render(user_role=selected_role)
    elif "5. Candidate Management" in selected_view:
        candidate_view.render(user_role=selected_role)
    elif "6. Resume Screening" in selected_view:
        screening_view.render(user_role=selected_role)
    elif "7. Shortlisting" in selected_view:
        shortlisting_view.render(user_role=selected_role)
    elif "8. Interview Management" in selected_view:
        interview_view.render(user_role=selected_role)
    elif "9. Communication Center" in selected_view:
        communication_view.render(user_role=selected_role)
    elif "10. Offer Management" in selected_view:
        offer_view.render(user_role=selected_role)
    elif "11. Employee Onboarding" in selected_view:
        onboarding_view.render(user_role=selected_role)
    elif "12. Employee Database" in selected_view:
        employee_db_view.render(user_role=selected_role)
    elif "13. HR Policies & SOPs" in selected_view:
        policy_view.render(user_role=selected_role)
    elif "14. Analytics & Reports" in selected_view:
        analytics_view.render(user_role=selected_role)
    elif "15. Settings & Audit Logs" in selected_view:
        settings_view.render(user_role=selected_role)
except Exception as e:
    st.error(f"An error occurred while loading this view: {e}")
    st.exception(e)

