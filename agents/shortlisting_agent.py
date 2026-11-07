"""
HR Nexus AI - Intelligent Candidate Shortlisting Agent
Ranks candidates, performs multi-candidate comparative analysis, identifies skill gaps,
recommends targeted assessments, and enforces HR human-in-the-loop approvals.
"""
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class ShortlistingAgent(BaseAIAgent):
    def get_ranked_candidates(self, requisition_id: int = None, min_score: float = 0.0,
                               stage_filter: str = None) -> list:
        """Fetch candidates ranked by overall match score with explainability details."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    c.id as candidate_id,
                    c.candidate_code,
                    c.full_name,
                    c.email,
                    c.phone,
                    c.location,
                    c.highest_education,
                    c.total_experience_years,
                    c.current_organization,
                    c.current_designation,
                    c.notice_period_days,
                    c.expected_salary,
                    a.id as application_id,
                    a.stage,
                    a.source,
                    a.applied_date,
                    jr.id as requisition_id,
                    jr.title as job_title,
                    jr.department,
                    COALESCE(sr.overall_match_score, 0) as overall_match_score,
                    COALESCE(sr.skills_match_score, 0) as skills_match_score,
                    COALESCE(sr.experience_match_score, 0) as experience_match_score,
                    COALESCE(sr.education_match_score, 0) as education_match_score,
                    sr.matching_skills,
                    sr.missing_skills,
                    sr.candidate_summary,
                    sr.verification_flags,
                    sr.recommendation,
                    sr.screening_rationale,
                    sr.human_reviewed
                FROM candidates c
                JOIN applications a ON c.id = a.candidate_id
                JOIN job_requisitions jr ON a.requisition_id = jr.id
                LEFT JOIN screening_results sr ON a.id = sr.application_id
                WHERE 1=1
            """
            params = []
            if requisition_id:
                query += " AND jr.id = ?"
                params.append(requisition_id)
            if min_score > 0:
                query += " AND COALESCE(sr.overall_match_score, 0) >= ?"
                params.append(min_score)
            if stage_filter and stage_filter != "All Stages":
                query += " AND a.stage = ?"
                params.append(stage_filter)

            query += " ORDER BY sr.overall_match_score DESC, c.total_experience_years DESC;"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def compare_candidates(self, candidate_ids: list, requisition_id: int) -> dict:
        """Generate side-by-side comparative analysis of selected candidates."""
        candidates = []
        with get_db() as conn:
            cursor = conn.cursor()
            for cid in candidate_ids:
                cursor.execute("""
                    SELECT c.*, a.id as application_id, a.stage,
                           sr.skills_match_score, sr.experience_match_score,
                           sr.education_match_score, sr.overall_match_score,
                           sr.matching_skills, sr.missing_skills, sr.candidate_summary,
                           sr.recommendation
                    FROM candidates c
                    JOIN applications a ON c.id = a.candidate_id
                    LEFT JOIN screening_results sr ON a.id = sr.application_id
                    WHERE c.id = ? AND a.requisition_id = ?;
                """, (cid, requisition_id))
                row = cursor.fetchone()
                if row:
                    candidates.append(dict(row))

        if not candidates:
            return {"summary": "No matching candidates found for comparison.", "matrix": []}

        # Build comparison summary
        best_candidate = max(candidates, key=lambda x: x.get('overall_match_score', 0))
        summary = (
            f"Comparison of {len(candidates)} candidates for requisition. "
            f"Top ranked candidate is {best_candidate.get('full_name')} with an overall match score of {best_candidate.get('overall_match_score')}%. "
            f"Recommended Next Action: Review interview availability and schedule Round 1 Technical Assessment."
        )

        return {
            "summary": summary,
            "candidates": candidates,
            "top_candidate": best_candidate
        }

    def update_candidate_stage(self, application_id: int, new_stage: str, notes: str = "", approved_by: str = "HR Manager") -> bool:
        """Update candidate pipeline stage with audit trail."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE applications
                SET stage = ?, status_notes = ?
                WHERE id = ?;
            """, (new_stage, notes, application_id))

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("CANDIDATE_STAGE_UPDATED", "Shortlisting", approved_by, f"Updated Application #{application_id} to {new_stage}"))
            return True

