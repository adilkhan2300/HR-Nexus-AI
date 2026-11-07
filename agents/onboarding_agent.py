"""
HR Nexus AI - Employee Onboarding Agent
Manages the end-to-end 4-phase onboarding lifecycle: Pre-Joining, Day 1, First Week, First 30 Days.
Generates employee IDs, tracks document verification SLAs, and automates onboarding progress.
"""
import random
from datetime import datetime, timedelta
from agents.base_agent import BaseAIAgent
from database.connection import get_db

STANDARD_ONBOARDING_TASKS = [
    # Pre-Joining
    ("Pre-Joining", "Offer Acceptance & Formal Confirmation", "Candidate must sign offer letter and confirm start date.", "Candidate", 5),
    ("Pre-Joining", "Identity Proof Submission (Passport / National ID)", "Upload verified government photo ID.", "Candidate", 7),
    ("Pre-Joining", "Address Proof Verification", "Submit recent utility bill or rental agreement.", "Candidate", 7),
    ("Pre-Joining", "Educational Certificates & Transcripts", "Upload highest degree diploma and marks transcripts.", "Candidate", 10),
    ("Pre-Joining", "Previous Employment Relieving & Experience Letters", "Submit relieving letter from most recent employer.", "Candidate", 10),
    ("Pre-Joining", "Direct Deposit & Statutory Tax Form", "Upload voided check and completed W-4/tax declaration.", "Candidate", 10),

    # Day 1
    ("Day 1", "Automated Welcome Email & Corporate Credentials", "Dispatch welcome packet and Google Workspace/Slack access.", "HR Operations", 1),
    ("Day 1", "Hardware Provisioning & IT Security Setup", "Issue MacBook/laptop, configure 2FA security tokens.", "IT Support", 1),
    ("Day 1", "HR Orientation & Company Policy Briefing", "60-minute session covering culture, benefits, leave SOP.", "HR Manager", 1),
    ("Day 1", "Department Introduction & Reporting Manager Welcome", "Initial 1-on-1 meeting with designated manager and team buddy.", "Reporting Manager", 1),
    ("Day 1", "HRMS Profile Activation & Attendance Registration", "Enroll biometric/remote access in attendance system.", "HR Operations", 1),

    # First Week
    ("First Week", "System Access Rights & Software Licenses", "Grant repo access, JIRA, cloud consoles as required.", "IT Support", 3),
    ("First Week", "Company SOPs & Security Compliance Training", "Complete mandatory data protection and anti-harassment training.", "Candidate", 5),
    ("First Week", "Departmental Training & Architecture Overview", "Deep dive into team workflows, codebase, and toolkits.", "Reporting Manager", 5),
    ("First Week", "Role & 90-Day Deliverables Alignment", "Document key milestones expected during the probationary period.", "Reporting Manager", 5),

    # First 30 Days
    ("First 30 Days", "Two-Week Check-in & Feedback Session", "Evaluate onboarding velocity, resolve any tooling blockers.", "HR Manager", 14),
    ("First 30 Days", "Independent Milestone Delivery", "Ship first feature, PRD draft, or operational deliverable.", "Reporting Manager", 25),
    ("First 30 Days", "Probation Month 1 Performance & Goals Review", "Formal 30-day performance review against probation KPIs.", "Reporting Manager", 30)
]

STANDARD_DOCUMENTS = [
    "Identity Proof (Passport/National ID)",
    "Residential Address Proof",
    "Highest Educational Degree Certificate",
    "Previous Employment Relieving Letter",
    "Statutory Tax Declaration (W-4 / PAN)",
    "Bank Account Direct Deposit Details"
]

class OnboardingAgent(BaseAIAgent):
    def initiate_onboarding(self, candidate_id: int, offer_id: int, approved_by: str = "HR Manager") -> dict:
        """
        Triggered when a candidate accepts an offer.
        Generates employee ID, creates master record, seeds 4-phase tasks and documents.
        """
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. Fetch candidate and offer details
            cursor.execute("""
                SELECT c.*, o.designation, o.department, o.reporting_manager,
                       o.joining_date, o.work_location, o.employment_type
                FROM candidates c
                JOIN offers o ON c.id = o.candidate_id
                WHERE c.id = ? AND o.id = ?;
            """, (candidate_id, offer_id))
            data = cursor.fetchone()
            if not data:
                return {"success": False, "error": "Candidate or Offer record not found."}

            data = dict(data)
            # 2. Generate unique Employee Code (e.g. EMP-2026-042)
            emp_code = f"EMP-2026-{random.randint(110, 999)}"
            company_email = f"{data['full_name'].lower().replace(' ', '.')}@hrnexus.ai"

            # 3. Create Employee record
            cursor.execute("""
                INSERT INTO employees (
                    employee_code, full_name, email, personal_phone,
                    department, designation, reporting_manager, joining_date,
                    work_location, employment_type, employment_status,
                    onboarding_progress, doc_verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Probation', 5, 'Pending');
            """, (
                emp_code, data['full_name'], company_email, data['phone'],
                data['department'], data['designation'], data['reporting_manager'],
                data['joining_date'], data['work_location'], data['employment_type']
            ))
            emp_id = cursor.lastrowid

            # 4. Create standard document placeholders
            for doc_type in STANDARD_DOCUMENTS:
                cursor.execute("""
                    INSERT INTO employee_documents (
                        employee_id, document_type, document_name, status
                    ) VALUES (?, ?, ?, 'Pending');
                """, (emp_id, doc_type, f"{doc_type.split()[0].lower()}_doc.pdf"))

            # 5. Populate standard 4-phase onboarding tasks
            jdate = datetime.strptime(data['joining_date'], "%Y-%m-%d") if isinstance(data['joining_date'], str) else datetime.now()
            for phase, title, desc, assigned, due_offset in STANDARD_ONBOARDING_TASKS:
                if phase == "Pre-Joining":
                    due_date = (jdate - timedelta(days=max(1, 10 - due_offset))).strftime("%Y-%m-%d")
                else:
                    due_date = (jdate + timedelta(days=due_offset)).strftime("%Y-%m-%d")

                assigned_person = data['full_name'] if assigned == "Candidate" else (
                    data['reporting_manager'] if assigned == "Reporting Manager" else approved_by
                )

                cursor.execute("""
                    INSERT INTO onboarding_tasks (
                        employee_id, phase, task_title, task_description,
                        assigned_to, due_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, 'Pending');
                """, (emp_id, phase, title, desc, assigned_person, due_date))

            # 6. Mark offer as 'Accepted' and application stage as 'Hired'
            cursor.execute("UPDATE offers SET offer_status = 'Accepted' WHERE id = ?;", (offer_id,))
            cursor.execute("UPDATE applications SET stage = 'Hired' WHERE candidate_id = ?;", (candidate_id,))

            # 7. Add Audit Log & Notification
            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("ONBOARDING_INITIATED", "Onboarding", approved_by, f"Initiated onboarding for {data['full_name']} ({emp_code})"))

            cursor.execute("""
                INSERT INTO notifications (title, message, recipient_role, priority)
                VALUES (?, ?, 'HR Manager', 'High');
            """, (f"Onboarding Started: {emp_code}", f"New employee record created for {data['full_name']}. 4-phase checklist generated.",))

            return {
                "success": True,
                "employee_id": emp_id,
                "employee_code": emp_code,
                "employee_email": company_email
            }

    def update_document_status(self, doc_id: int, new_status: str, notes: str, verified_by: str = "HR Manager") -> bool:
        """Update employee document verification status."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE employee_documents
                SET status = ?, verification_notes = ?, verified_by = ?, verified_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (new_status, notes, verified_by, doc_id))

            # Recalculate document overall status for employee
            cursor.execute("SELECT employee_id FROM employee_documents WHERE id = ?;", (doc_id,))
            row = cursor.fetchone()
            if row:
                emp_id = row['employee_id']
                cursor.execute("SELECT status FROM employee_documents WHERE employee_id = ?;", (emp_id,))
                statuses = [r['status'] for r in cursor.fetchall()]
                if all(s == 'Verified' for s in statuses):
                    overall_doc = 'Verified'
                elif any(s == 'Rejected' for s in statuses):
                    overall_doc = 'Rejected'
                elif any(s in ['Submitted', 'Under Verification', 'Verified'] for s in statuses):
                    overall_doc = 'Partial'
                else:
                    overall_doc = 'Pending'

                cursor.execute("UPDATE employees SET doc_verification_status = ? WHERE id = ?;", (overall_doc, emp_id))
            return True

    def update_task_status(self, task_id: int, new_status: str, completed_by: str = "HR Manager") -> bool:
        """Mark task status and recalculate employee overall onboarding progress %."""
        with get_db() as conn:
            cursor = conn.cursor()
            completed_at = "CURRENT_TIMESTAMP" if new_status == "Completed" else "NULL"
            cursor.execute(f"""
                UPDATE onboarding_tasks
                SET status = ?, completed_by = ?, completed_at = {completed_at}
                WHERE id = ?;
            """, (new_status, completed_by, task_id))

            # Recalculate employee onboarding progress
            cursor.execute("SELECT employee_id FROM onboarding_tasks WHERE id = ?;", (task_id,))
            row = cursor.fetchone()
            if row:
                emp_id = row['employee_id']
                cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as done FROM onboarding_tasks WHERE employee_id = ?;", (emp_id,))
                stats = cursor.fetchone()
                total = stats['total'] or 1
                done = stats['done'] or 0
                progress = int((done / total) * 100)
                cursor.execute("UPDATE employees SET onboarding_progress = ? WHERE id = ?;", (progress, emp_id))
            return True

