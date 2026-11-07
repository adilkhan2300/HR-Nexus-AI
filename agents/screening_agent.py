"""
HR Nexus AI - AI Resume Screening & Parsing Agent
Calculates explainable, job-relevant match scores across Skills, Experience, and Education.
Strictly safeguards against protected attributes (zero bias).
Generates transparent reports with human-in-the-loop governance.
"""
import re
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class ScreeningAgent(BaseAIAgent):
    def screen_candidate(self, candidate_data: dict, job_data: dict) -> dict:
        """
        Screen candidate against job requirements using transparent scoring.
        Scoring Criteria:
          - Skills Match: 50%
          - Experience Match: 30%
          - Education Match: 20%
        """
        # 1. Skills Matching
        job_tech_skills = [s.strip().lower() for s in (job_data.get('technical_skills') or '').split(',') if s.strip()]
        job_soft_skills = [s.strip().lower() for s in (job_data.get('soft_skills') or '').split(',') if s.strip()]
        all_required_skills = list(set(job_tech_skills + job_soft_skills))

        cand_tech = [s.strip().lower() for s in candidate_data.get('technical_skills', [])]
        cand_soft = [s.strip().lower() for s in candidate_data.get('soft_skills', [])]
        all_cand_skills = list(set(cand_tech + cand_soft))

        matching_skills = []
        missing_skills = []

        if all_required_skills:
            for skill in all_required_skills:
                # check exact or partial substring match
                if any(skill in cs or cs in skill for cs in all_cand_skills):
                    matching_skills.append(skill.title())
                else:
                    missing_skills.append(skill.title())
            skills_score = round((len(matching_skills) / len(all_required_skills)) * 100, 1)
        else:
            skills_score = 80.0
            matching_skills = [s.title() for s in cand_tech[:5]]

        # 2. Experience Matching
        # Parse required exp like "4-7 Years" or "3 Years"
        req_exp_str = job_data.get('experience_required', '3-5 Years')
        exp_nums = re.findall(r'(\d+)', req_exp_str)
        min_exp = float(exp_nums[0]) if exp_nums else 3.0
        cand_exp = float(candidate_data.get('total_experience_years', 0))

        if cand_exp >= min_exp:
            # Full score if meets or exceeds minimum
            exp_score = min(100.0, round(90.0 + min(10.0, (cand_exp - min_exp) * 5), 1))
        else:
            exp_score = round(max(30.0, (cand_exp / min_exp) * 90.0), 1)

        # 3. Education Matching
        cand_edu = (candidate_data.get('highest_education') or '').lower()
        req_qual = (job_data.get('qualifications') or '').lower()

        edu_score = 75.0
        if any(deg in cand_edu for deg in ['ph.d', 'phd', 'doctorate']):
            edu_score = 100.0
        elif any(deg in cand_edu for deg in ['m.s', 'master', 'mba', 'm.tech']):
            edu_score = 95.0
        elif any(deg in cand_edu for deg in ['b.s', 'bachelor', 'b.tech', 'b.a', 'bba']):
            edu_score = 90.0
        elif 'diploma' in cand_edu or 'associate' in cand_edu:
            edu_score = 70.0

        # 4. Overall Weighted Score
        overall_score = round((skills_score * 0.50) + (exp_score * 0.30) + (edu_score * 0.20), 1)

        # 5. Verification Flags
        verification_flags = []
        if cand_exp < min_exp:
            verification_flags.append(f"Experience ({cand_exp} yrs) is below stated role minimum ({min_exp} yrs).")
        if candidate_data.get('notice_period_days', 30) > 60:
            verification_flags.append(f"Extended notice period of {candidate_data.get('notice_period_days')} days.")
        if not candidate_data.get('phone') or candidate_data.get('phone') == '+1 555-0199':
            verification_flags.append("Direct contact telephone number needs verification.")
        if candidate_data.get('certifications'):
            verification_flags.append(f"Verify credentials for: {', '.join(candidate_data.get('certifications'))}.")

        # 6. Recommendation logic (Human-in-the-loop safeguard)
        if overall_score >= 88.0:
            recommendation = "Strong Recommend for Interview"
        elif overall_score >= 75.0:
            recommendation = "Recommend for Interview"
        elif overall_score >= 60.0:
            recommendation = "Consider for Alternate Role / Review"
        else:
            recommendation = "Flagged for Manual HR Review"

        rationale = (
            f"Candidate achieved {overall_score}% overall compatibility ({skills_score}% skills, "
            f"{exp_score}% experience, {edu_score}% education). "
            f"Matches {len(matching_skills)} of {len(all_required_skills)} required competencies. "
            f"Experience: {cand_exp} years against requirement of {req_exp_str}."
        )

        return {
            "candidate_id": candidate_data.get('id'),
            "candidate_name": candidate_data.get('full_name'),
            "skills_match_score": skills_score,
            "experience_match_score": exp_score,
            "education_match_score": edu_score,
            "overall_match_score": overall_score,
            "matching_skills": ", ".join(matching_skills[:8]) if matching_skills else "None explicitly listed",
            "missing_skills": ", ".join(missing_skills[:6]) if missing_skills else "None",
            "candidate_summary": candidate_data.get('candidate_summary', ''),
            "verification_flags": "; ".join(verification_flags) if verification_flags else "None. Standard verification required.",
            "recommendation": recommendation,
            "screening_rationale": rationale
        }

    def save_screening_result(self, application_id: int, candidate_id: int, requisition_id: int, result: dict, reviewed_by: str = None) -> int:
        """Persist or update screening result in database."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO screening_results (
                    application_id, candidate_id, requisition_id,
                    skills_match_score, experience_match_score, education_match_score, overall_match_score,
                    matching_skills, missing_skills, candidate_summary, verification_flags,
                    recommendation, screening_rationale, human_reviewed, reviewed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(application_id) DO UPDATE SET
                    skills_match_score=excluded.skills_match_score,
                    experience_match_score=excluded.experience_match_score,
                    education_match_score=excluded.education_match_score,
                    overall_match_score=excluded.overall_match_score,
                    matching_skills=excluded.matching_skills,
                    missing_skills=excluded.missing_skills,
                    candidate_summary=excluded.candidate_summary,
                    verification_flags=excluded.verification_flags,
                    recommendation=excluded.recommendation,
                    screening_rationale=excluded.screening_rationale,
                    screened_at=CURRENT_TIMESTAMP;
            """, (
                application_id, candidate_id, requisition_id,
                result['skills_match_score'], result['experience_match_score'],
                result['education_match_score'], result['overall_match_score'],
                result['matching_skills'], result['missing_skills'],
                result['candidate_summary'], result['verification_flags'],
                result['recommendation'], result['screening_rationale'],
                1 if reviewed_by else 0, reviewed_by
            ))
            return cursor.lastrowid

