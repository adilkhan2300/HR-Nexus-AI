"""
HR Nexus AI - Global Configuration and Constants
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "hr_nexus.db"
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DOCS_DIR = BASE_DIR / "generated_docs"
SAMPLE_RESUMES_DIR = BASE_DIR / "sample_resumes"

for d in [UPLOAD_DIR, GENERATED_DOCS_DIR, SAMPLE_RESUMES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Application Meta
APP_NAME = "HR Nexus AI"
APP_SUBTITLE = "Intelligent Recruitment & Employee Onboarding Agent"
APP_VERSION = "2.0.0"

# User Roles
ROLES = {
    "ADMIN": "Admin",
    "HR_MANAGER": "HR Manager",
    "INTERVIEWER": "Interviewer / Dept Manager"
}

# Candidate Pipeline Stages (12 stages specified)
PIPELINE_STAGES = [
    "Applied",
    "Resume Screening",
    "Shortlisted",
    "Assessment",
    "Interview Scheduled",
    "Interview Completed",
    "Selected",
    "Offer Released",
    "Offer Accepted",
    "Hired",
    "Rejected",
    "Talent Pool"
]

STAGE_COLORS = {
    "Applied": "#94a3b8",
    "Resume Screening": "#38bdf8",
    "Shortlisted": "#6366f1",
    "Assessment": "#a855f7",
    "Interview Scheduled": "#f59e0b",
    "Interview Completed": "#ec4899",
    "Selected": "#10b981",
    "Offer Released": "#06b6d4",
    "Offer Accepted": "#059669",
    "Hired": "#16a34a",
    "Rejected": "#ef4444",
    "Talent Pool": "#64748b"
}

# Onboarding Checklist Phases
ONBOARDING_PHASES = [
    "Pre-Joining",
    "Day 1",
    "First Week",
    "First 30 Days"
]

DOCUMENT_STATUSES = [
    "Pending",
    "Submitted",
    "Under Verification",
    "Verified",
    "Rejected"
]

TASK_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
    "Overdue"
]

# Requisition Priorities
PRIORITIES = ["Low", "Medium", "High", "Critical"]

# Employment Types
EMPLOYMENT_TYPES = ["Full-Time", "Part-Time", "Contract", "Internship", "Remote"]

# Departments
DEPARTMENTS = [
    "Engineering & Technology",
    "Human Resources",
    "Product & Design",
    "Sales & Marketing",
    "Finance & Accounting",
    "Operations & Legal"
]

