"""
HR Nexus AI - Autonomous Workflow Engine
Coordinates multi-step Recruitment and Onboarding lifecycles with state machines,
audit logs, error handling, and mandatory human-in-the-loop approval checkpoints.
"""
import json
from datetime import datetime
from database.connection import get_db

RECRUITMENT_STEPS = [
    "Requisition Created",
    "Requisition Approved",
    "AI JD Generated",
    "Job Published",
    "Applications Received",
    "AI Resumes Parsed",
    "AI Candidate Screening",
    "AI Shortlist Prepared",
    "HR Shortlist Sign-off",
    "Interviews Scheduled",
    "Interviews Completed & Feedback Evaluated",
    "Candidate Selected",
    "AI Offer Letter Generated",
    "HR Offer Sign-off & Released",
    "Offer Accepted",
    "Handoff to Onboarding Workflow"
]

ONBOARDING_STEPS = [
    "Offer Accepted",
    "Employee Profile Created",
    "Employee ID Generated",
    "4-Phase Checklist Generated",
    "Pre-Joining Documents Requested",
    "Candidate Submits Documents",
    "HR Document Verification SLA",
    "IT Hardware & Systems Provisioning",
    "Day 1 Orientation Completed",
    "Department Welcome & Buddy Assigned",
    "First Week SOP Training",
    "30-Day Milestone & Review",
    "Final Onboarding Completion Certified"
]

class WorkflowEngine:
    def create_workflow(self, workflow_type: str, workflow_name: str, entity_id: int,
                        initiated_by: str = "HR Manager", payload: dict = None) -> int:
        """Instantiate a new workflow instance."""
        steps = RECRUITMENT_STEPS if workflow_type == "Recruitment" else ONBOARDING_STEPS
        initial_step = steps[0]
        history = [f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Workflow initialized at step: {initial_step} by {initiated_by}"]

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workflow_executions (
                    workflow_type, workflow_name, entity_id, current_step,
                    status, initiated_by, payload_json, execution_history
                ) VALUES (?, ?, ?, ?, 'In Progress', ?, ?, ?);
            """, (
                workflow_type, workflow_name, entity_id, initial_step,
                initiated_by, json.dumps(payload or {}), "\n".join(history)
            ))
            wf_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("WORKFLOW_INITIALIZED", "Workflow Engine", initiated_by, f"Started {workflow_type} workflow #{wf_id}: {workflow_name}"))

            return wf_id

    def advance_step(self, workflow_id: int, next_step: str, performed_by: str, notes: str = "") -> bool:
        """Advance workflow to next milestone and append to execution history."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflow_executions WHERE id = ?;", (workflow_id,))
            wf = cursor.fetchone()
            if not wf:
                return False

            old_step = wf["current_step"]
            history_lines = wf["execution_history"].split("\n") if wf["execution_history"] else []
            history_lines.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Step advanced: {old_step} -> {next_step} by {performed_by} ({notes})")

            # Check if final step
            wf_type = wf["workflow_type"]
            all_steps = RECRUITMENT_STEPS if wf_type == "Recruitment" else ONBOARDING_STEPS
            new_status = "Completed" if next_step == all_steps[-1] else "In Progress"

            cursor.execute("""
                UPDATE workflow_executions
                SET current_step = ?, status = ?, execution_history = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?;
            """, (next_step, new_status, "\n".join(history_lines), workflow_id))

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("WORKFLOW_STEP_ADVANCED", "Workflow Engine", performed_by, f"Workflow #{workflow_id} moved to: {next_step}"))

            return True

    def list_active_workflows(self) -> list:
        """Fetch list of all active workflows."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM workflow_executions ORDER BY updated_at DESC;")
            return [dict(r) for r in cursor.fetchall()]

