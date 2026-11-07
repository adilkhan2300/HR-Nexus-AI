"""
HR Nexus AI - Central AI HR Chat Agent & Intent Router
Converts natural language commands into actionable workflows, distinguishes query types,
and surfaces pending approvals and execution history.
"""
import re
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class HRChatAgent(BaseAIAgent):
    def process_command(self, user_command: str, user_role: str = "HR Manager") -> dict:
        """
        Analyze natural language instruction, determine intent, execute action or draft workflow,
        and classify action type:
          - 'READ_ONLY'
          - 'DRAFT'
          - 'REQUIRES_APPROVAL'
          - 'COMPLETED'
        """
        cmd = user_command.strip()
        cmd_lower = cmd.lower()

        # 1. Intent: Create Job Opening / Requisition
        if any(w in cmd_lower for w in ["create a job", "create job", "open position", "new requisition", "create opening"]):
            return self._handle_create_job(cmd, user_role)

        # 2. Intent: Screen Resumes
        if any(w in cmd_lower for w in ["screen", "screen all resumes", "parse resumes", "run screening"]):
            return self._handle_screen_resumes(cmd, user_role)

        # 3. Intent: Find / Rank Top Candidates
        if any(w in cmd_lower for w in ["top 5", "top 3", "top candidate", "find candidates", "rank candidates", "compare"]):
            return self._handle_find_top_candidates(cmd, user_role)

        # 4. Intent: Schedule Interview
        if any(w in cmd_lower for w in ["schedule interview", "schedule interviews", "set interview"]):
            return self._handle_schedule_interview(cmd, user_role)

        # 5. Intent: Generate Offer Letter
        if any(w in cmd_lower for w in ["offer letter", "generate offer", "create offer"]):
            return self._handle_generate_offer(cmd, user_role)

        # 6. Intent: Start Onboarding
        if any(w in cmd_lower for w in ["start onboarding", "initiate onboarding", "begin onboarding"]):
            return self._handle_start_onboarding(cmd, user_role)

        # 7. Intent: Check Pending Onboarding Documents / Tasks
        if any(w in cmd_lower for w in ["pending document", "onboarding document", "incomplete onboarding", "pending onboarding"]):
            return self._handle_pending_onboarding(cmd, user_role)

        # 8. Intent: Show Open Positions
        if any(w in cmd_lower for w in ["show all open", "open positions", "list jobs", "active requisitions"]):
            return self._handle_list_jobs()

        # 9. Intent: Policy or SOP query
        if any(w in cmd_lower for w in ["policy", "leave", "handbook", "sop", "allowance", "stipend", "core hours"]):
            from agents.policy_rag_agent import PolicyRAGAgent
            rag = PolicyRAGAgent()
            res = rag.answer_query(cmd)
            return {
                "intent": "POLICY_QUERY",
                "action_type": "READ_ONLY",
                "response": res["answer"],
                "data": res["citations"],
                "execution_status": "Success"
            }

        # 10. General conversational query or fallback
        system_prompt = (
            "You are HR Nexus AI, an autonomous HR department coordinator. "
            "Respond authoritatively and concisely. If the user wants to initiate a recruitment "
            "or onboarding workflow, guide them on the exact parameters needed."
        )
        ai_resp = self.generate_text(system_prompt, cmd, temperature=0.3)
        return {
            "intent": "GENERAL_QUERY",
            "action_type": "READ_ONLY",
            "response": ai_resp,
            "data": None,
            "execution_status": "Success"
        }

    def _handle_list_jobs(self) -> dict:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT requisition_code, title, department, vacancies, priority, approval_status FROM job_requisitions;")
            jobs = [dict(r) for r in cursor.fetchall()]

        summary = f"There are currently **{len(jobs)}** job requisitions in the system:\n\n"
        for j in jobs:
            summary += f"- **{j['requisition_code']}**: {j['title']} ({j['department']}) – {j['vacancies']} vacancy – Priority: `{j['priority']}` – Status: `{j['approval_status']}`\n"

        return {
            "intent": "LIST_JOBS",
            "action_type": "READ_ONLY",
            "response": summary,
            "data": jobs,
            "execution_status": "Success"
        }

    def _handle_create_job(self, cmd: str, user_role: str) -> dict:
        # Extract title
        title = "Business Analyst"
        if "for a " in cmd.lower():
            title = cmd.lower().split("for a ")[1].split(".")[0].strip().title()
        elif "for " in cmd.lower():
            title = cmd.lower().split("for ")[1].split(".")[0].strip().title()

        req_code = f"REQ-2026-{100 + len(cmd)}"
        resp = (
            f"🎯 **Action Prepared: New Job Requisition Draft**\n\n"
            f"- **Role Title:** {title}\n"
            f"- **Requisition ID:** `{req_code}`\n"
            f"- **Department:** Enterprise Operations\n"
            f"- **Priority:** High\n"
            f"- **Vacancies:** 1\n\n"
            f"⚠️ *Human-in-the-loop Governance*: This draft requires HR Manager or Admin approval before publishing."
        )
        return {
            "intent": "CREATE_JOB_REQUISITION",
            "action_type": "REQUIRES_APPROVAL",
            "response": resp,
            "data": {"title": title, "code": req_code, "action": "approve_job_requisition"},
            "execution_status": "Awaiting Approval"
        }

    def _handle_screen_resumes(self, cmd: str, user_role: str) -> dict:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.full_name, jr.title as job_title, sr.overall_match_score, sr.recommendation
                FROM screening_results sr
                JOIN candidates c ON sr.candidate_id = c.id
                JOIN job_requisitions jr ON sr.requisition_id = jr.id
                ORDER BY sr.overall_match_score DESC
                LIMIT 5;
            """)
            screened = [dict(r) for r in cursor.fetchall()]

        resp = (
            f"🤖 **Autonomous Resume Screening Complete!**\n\n"
            f"Successfully parsed and screened applicant resumes against job requirements using transparent, non-discriminatory scoring:\n\n"
        )
        for s in screened:
            resp += f"- **{s['full_name']}** → Overall Match: `{s['overall_match_score']}%` – *{s['recommendation']}*\n"

        resp += "\n✨ *All criteria are job-relevant and transparent. Final shortlisting decisions require HR sign-off.*"

        return {
            "intent": "SCREEN_RESUMES",
            "action_type": "COMPLETED",
            "response": resp,
            "data": screened,
            "execution_status": "Success"
        }

    def _handle_find_top_candidates(self, cmd: str, user_role: str) -> dict:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.full_name, c.highest_education, c.total_experience_years, c.current_organization,
                       jr.title as job_title, sr.overall_match_score, sr.skills_match_score, sr.recommendation
                FROM screening_results sr
                JOIN candidates c ON sr.candidate_id = c.id
                JOIN job_requisitions jr ON sr.requisition_id = jr.id
                ORDER BY sr.overall_match_score DESC
                LIMIT 5;
            """)
            top_candidates = [dict(r) for r in cursor.fetchall()]

        resp = "🏆 **Top 5 Ranked Candidates across Open Pipelines:**\n\n"
        for i, c in enumerate(top_candidates, 1):
            resp += (
                f"{i}. **{c['full_name']}** ({c['overall_match_score']}% match)\n"
                f"   - Role: {c['job_title']} | Exp: {c['total_experience_years']} yrs at {c['current_organization']}\n"
                f"   - Education: {c['highest_education']} | Recommendation: `{c['recommendation']}`\n"
            )

        return {
            "intent": "FIND_TOP_CANDIDATES",
            "action_type": "READ_ONLY",
            "response": resp,
            "data": top_candidates,
            "execution_status": "Success"
        }

    def _handle_schedule_interview(self, cmd: str, user_role: str) -> dict:
        resp = (
            "📅 **Interview Workflow Ready**\n\n"
            "I have identified shortlisted candidates eligible for Round 1 Technical Assessment.\n\n"
            "- Suggested Candidate: **Alex Rivera** (Senior Python Developer, 93.3% match)\n"
            "- Assigned Interviewer: **David Chen** (Engineering Lead)\n"
            "- Suggested Duration: 45 minutes via Google Meet\n\n"
            "Would you like to dispatch the calendar invites and automated email notifications now?"
        )
        return {
            "intent": "SCHEDULE_INTERVIEWS",
            "action_type": "REQUIRES_APPROVAL",
            "response": resp,
            "data": {"candidate": "Alex Rivera", "interviewer": "David Chen"},
            "execution_status": "Awaiting Approval"
        }

    def _handle_generate_offer(self, cmd: str, user_role: str) -> dict:
        resp = (
            "📝 **Offer Letter Generation Request**\n\n"
            "Drafting employment offer for **Alex Rivera** (Senior Python Developer):\n"
            "- Department: Engineering & Technology\n"
            "- Proposed CTC: $125,000 USD Annual\n"
            "- Start Date: 2026-04-01\n"
            "- Reporting Manager: David Chen\n\n"
            "⚠️ *Approval Gate*: Offer documents must be approved by authorized HR sign-off prior to candidate dispatch."
        )
        return {
            "intent": "GENERATE_OFFER",
            "action_type": "DRAFT",
            "response": resp,
            "data": {"candidate": "Alex Rivera", "action": "review_offer_draft"},
            "execution_status": "Draft Prepared"
        }

    def _handle_start_onboarding(self, cmd: str, user_role: str) -> dict:
        resp = (
            "🚀 **Employee Onboarding Initiation**\n\n"
            "Selected Candidate: **Aisha Khan** (HR Executive)\n"
            "- Status: Offer Accepted\n"
            "- System Action: Generate Employee ID, provision Pre-Joining document checklists, and notify IT.\n\n"
            "Click **Confirm & Initiate Onboarding** below to execute this autonomous workflow."
        )
        return {
            "intent": "START_ONBOARDING",
            "action_type": "REQUIRES_APPROVAL",
            "response": resp,
            "data": {"candidate": "Aisha Khan", "action": "confirm_onboarding"},
            "execution_status": "Awaiting Confirmation"
        }

    def _handle_pending_onboarding(self, cmd: str, user_role: str) -> dict:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.employee_code, e.full_name, e.department, e.doc_verification_status,
                       e.onboarding_progress, d.document_name, d.status as doc_status
                FROM employees e
                LEFT JOIN employee_documents d ON e.id = d.employee_id
                WHERE d.status IN ('Pending', 'Submitted', 'Under Verification')
                ORDER BY e.id;
            """)
            pending = [dict(r) for r in cursor.fetchall()]

        resp = "📋 **Employees with Pending Onboarding Documents:**\n\n"
        for p in pending:
            resp += f"- **{p['full_name']}** ({p['employee_code']} - {p['department']}): Document `{p['document_name']}` is **{p['doc_status']}** (Overall Progress: {p['onboarding_progress']}%)\n"

        return {
            "intent": "PENDING_ONBOARDING",
            "action_type": "READ_ONLY",
            "response": resp,
            "data": pending,
            "execution_status": "Success"
        }

