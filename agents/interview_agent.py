"""
HR Nexus AI - Interview Management Agent
Schedules rounds, collects multi-dimensional feedback, generates role-specific STAR question banks,
and provides multi-round evaluation summaries while preserving human authority.
"""
import random
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class InterviewAgent(BaseAIAgent):
    def generate_interview_questions(self, job_title: str, required_skills: str, round_type: str = "Technical") -> dict:
        """Generate structured question bank with STAR behavioral and technical questions."""
        system_prompt = (
            "You are a Senior Technical Interview Architect. Generate structured interview questions "
            "using the STAR framework (Situation, Task, Action, Result) and evaluation rubrics."
        )
        user_prompt = f"""
Role: {job_title}
Key Skills: {required_skills}
Round Type: {round_type}

Generate:
1. Three Technical/Domain deep-dive questions with expected answer criteria.
2. Two Behavioral questions using STAR methodology.
3. Scoring Rubric (1-10 scale) covering Technical, Communication, Problem Solving, and Culture Fit.
"""
        generated = self.generate_text(system_prompt, user_prompt, temperature=0.4)

        # Fallback question sets if needed
        questions = [
            {
                "category": "Technical Architecture",
                "question": f"How do you design a scalable service around {required_skills.split(',')[0] if required_skills else 'core backend components'} with minimal latency and high fault tolerance?",
                "evaluation_guide": "Look for modular decoupling, caching strategies (Redis), connection pooling, and error boundaries."
            },
            {
                "category": "Debugging & Incident Response",
                "question": "Walk through an incident where a production service was throwing intermittent 500 errors. How did you triage, monitor metrics, and implement root-cause fixes?",
                "evaluation_guide": "Candidate should discuss log tracing, metric analysis, rollback procedures, and post-mortem creation."
            },
            {
                "category": "STAR Behavioral (Cross-functional Influence)",
                "question": "Describe a scenario where a product manager asked for a deadline you knew would sacrifice code quality or security. How did you negotiate?",
                "evaluation_guide": "STAR: Evaluates situation clarity, constructive compromise, data-backed reasoning, and relationship preservation."
            },
            {
                "category": "STAR Behavioral (Failure & Growth)",
                "question": "Tell us about a technical or architectural mistake you made in the past. What was the impact and what guardrail did you put in place afterwards?",
                "evaluation_guide": "Candidate must show genuine accountability without shifting blame, followed by automated linting/tests."
            }
        ]

        return {
            "job_title": job_title,
            "round_type": round_type,
            "generated_text": generated,
            "questions": questions
        }

    def schedule_interview(self, application_id: int, candidate_id: int, requisition_id: int,
                           round_name: str, round_number: int, interviewer_name: str,
                           interviewer_email: str, scheduled_time: str, duration_minutes: int = 45,
                           meeting_link: str = "") -> int:
        """Schedule a new interview round."""
        interview_code = f"INT-{random.randint(100, 999)}"
        if not meeting_link:
            meeting_link = f"https://meet.google.com/hrn-{random.randint(100,999)}-{random.randint(100,999)}"

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interviews (
                    interview_code, application_id, candidate_id, requisition_id,
                    round_name, round_number, interviewer_name, interviewer_email,
                    scheduled_time, duration_minutes, meeting_link, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Scheduled');
            """, (
                interview_code, application_id, candidate_id, requisition_id,
                round_name, round_number, interviewer_name, interviewer_email,
                scheduled_time, duration_minutes, meeting_link
            ))
            int_id = cursor.lastrowid

            # Update application stage to 'Interview Scheduled'
            cursor.execute("""
                UPDATE applications SET stage = 'Interview Scheduled' WHERE id = ?;
            """, (application_id,))

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("INTERVIEW_SCHEDULED", "Interviews", "HR Manager", f"Scheduled {round_name} for candidate #{candidate_id} on {scheduled_time}"))

            return int_id

    def submit_feedback(self, interview_id: int, interviewer_name: str, tech_score: float,
                        comm_score: float, prob_score: float, comp_score: float,
                        exp_score: float, strengths: str, weaknesses: str, comments: str,
                        recommendation: str) -> int:
        """Record structured multi-parameter interview evaluation."""
        overall = round((tech_score + comm_score + prob_score + comp_score + exp_score) / 5.0, 1)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interview_feedback (
                    interview_id, interviewer_name, technical_score, communication_score,
                    problem_solving_score, competency_score, experience_score, overall_rating,
                    strengths, weaknesses, detailed_comments, recommendation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                interview_id, interviewer_name, tech_score, comm_score, prob_score,
                comp_score, exp_score, overall, strengths, weaknesses, comments, recommendation
            ))
            fb_id = cursor.lastrowid

            # Mark interview as Completed
            cursor.execute("""
                UPDATE interviews SET status = 'Completed', attendance_confirmed = 1 WHERE id = ?;
            """, (interview_id,))

            # Also update application stage to 'Interview Completed'
            cursor.execute("""
                UPDATE applications SET stage = 'Interview Completed'
                WHERE id = (SELECT application_id FROM interviews WHERE id = ?);
            """, (interview_id,))

            return fb_id

