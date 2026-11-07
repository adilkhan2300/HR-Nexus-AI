"""
HR Nexus AI - View 12: Central Employee Master Database
"""
import streamlit as st
import pandas as pd
from database.connection import get_db
from config import DEPARTMENTS, EMPLOYMENT_TYPES
from services.auth_service import AuthService

def render(user_role: str = "HR Manager"):
    st.markdown("### 🏢 Central Employee Master Database")
    st.markdown("Central repository of organizational personnel with role-based data privacy controls and onboarding audit trails.")

    can_view_confidential = AuthService.check_permission(user_role, "can_view_confidential_salary")

    # Search and Filter
    c_s, c_d = st.columns([2, 1])
    with c_s:
        search_term = st.text_input("🔍 Search by name, employee code, or designation:", "")
    with c_d:
        filter_dept = st.selectbox("Filter Department:", ["All Departments"] + DEPARTMENTS)

    with get_db() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM employees WHERE 1=1"
        params = []
        if search_term:
            query += " AND (full_name LIKE ? OR employee_code LIKE ? OR designation LIKE ?)"
            term = f"%{search_term}%"
            params.extend([term, term, term])
        if filter_dept != "All Departments":
            query += " AND department = ?"
            params.append(filter_dept)
        query += " ORDER BY id DESC;"

        cursor.execute(query, params)
        employees = [dict(r) for r in cursor.fetchall()]

    if employees:
        df_emps = pd.DataFrame(employees)
        display_cols = ['employee_code', 'full_name', 'department', 'designation', 'reporting_manager', 'joining_date', 'employment_status', 'onboarding_progress', 'doc_verification_status']
        st.dataframe(df_emps[display_cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 👤 Employee Profile Inspector & Details")
        emp_select_map = {f"{e['full_name']} ({e['employee_code']})": e for e in employees}
        sel_label = st.selectbox("Select Employee to Inspect:", list(emp_select_map.keys()))
        emp = emp_select_map[sel_label]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Employee Code:** `{emp['employee_code']}`")
            st.markdown(f"**Full Name:** {emp['full_name']}")
            st.markdown(f"**Company Email:** {emp['email']}")
            st.markdown(f"**Personal Phone:** {emp['personal_phone']}")
        with col2:
            st.markdown(f"**Department:** {emp['department']}")
            st.markdown(f"**Designation:** {emp['designation']}")
            st.markdown(f"**Reporting Manager:** {emp['reporting_manager']}")
            st.markdown(f"**Work Location:** {emp['work_location']}")
        with col3:
            st.markdown(f"**Joining Date:** {emp['joining_date']}")
            st.markdown(f"**Employment Type:** {emp['employment_type']}")
            st.markdown(f"**Status:** `{emp['employment_status']}`")
            st.markdown(f"**Doc Status:** `{emp['doc_verification_status']}`")

        # Confidential compensation notice
        if not can_view_confidential:
            st.info("🔒 *Confidential compensation details and tax documents are restricted for your current access role.*")

        # Edit status
        if user_role in ['Admin', 'HR Manager']:
            with st.expander("✏️ Edit Employment Status"):
                new_status = st.selectbox("Update Status:", ["Probation", "Active", "Confirmed", "Resigned", "Terminated"], index=["Probation", "Active", "Confirmed", "Resigned", "Terminated"].index(emp['employment_status']))
                if st.button("Save Status Update"):
                    with get_db() as conn:
                        conn.cursor().execute("UPDATE employees SET employment_status = ? WHERE id = ?;", (new_status, emp['id']))
                        conn.cursor().execute("INSERT INTO audit_logs (user_action, module, performed_by, details) VALUES (?, ?, ?, ?);",
                                              ("EMPLOYEE_STATUS_UPDATED", "Employee DB", user_role, f"Updated {emp['employee_code']} to {new_status}"))
                    st.success("Employee record updated successfully!")
                    st.rerun()
    else:
        st.info("No matching employees found.")

