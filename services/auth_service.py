"""
HR Nexus AI - Authentication & Role-Based Access Control (RBAC) Service
Defines permissions for Admin, HR Manager, and Interviewer / Dept Manager.
"""
from config import ROLES
from database.connection import get_db

ROLE_PERMISSIONS = {
    "Admin": {
        "can_manage_users": True,
        "can_create_requisition": True,
        "can_approve_requisition": True,
        "can_screen_candidates": True,
        "can_shortlist_candidates": True,
        "can_schedule_interviews": True,
        "can_submit_feedback": True,
        "can_generate_offers": True,
        "can_approve_offers": True,
        "can_manage_onboarding": True,
        "can_verify_documents": True,
        "can_view_confidential_salary": True,
        "can_view_analytics": True,
        "can_manage_settings": True
    },
    "HR Manager": {
        "can_manage_users": False,
        "can_create_requisition": True,
        "can_approve_requisition": True,
        "can_screen_candidates": True,
        "can_shortlist_candidates": True,
        "can_schedule_interviews": True,
        "can_submit_feedback": True,
        "can_generate_offers": True,
        "can_approve_offers": True,
        "can_manage_onboarding": True,
        "can_verify_documents": True,
        "can_view_confidential_salary": True,
        "can_view_analytics": True,
        "can_manage_settings": False
    },
    "Interviewer / Dept Manager": {
        "can_manage_users": False,
        "can_create_requisition": False,
        "can_approve_requisition": False,
        "can_screen_candidates": False,
        "can_shortlist_candidates": False,
        "can_schedule_interviews": False,
        "can_submit_feedback": True,
        "can_generate_offers": False,
        "can_approve_offers": False,
        "can_manage_onboarding": False,
        "can_verify_documents": False,
        "can_view_confidential_salary": False,
        "can_view_analytics": False,
        "can_manage_settings": False
    }
}

class AuthService:
    @staticmethod
    def get_users():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, full_name, email, role, department FROM users;")
            return [dict(r) for r in cursor.fetchall()]

    @staticmethod
    def check_permission(role: str, permission_key: str) -> bool:
        perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["HR Manager"])
        return perms.get(permission_key, False)

