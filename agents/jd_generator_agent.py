"""
HR Nexus AI - Job Description Generator Agent
Generates comprehensive enterprise JDs from role parameters.
"""
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class JDGeneratorAgent(BaseAIAgent):
    def generate_job_description(self, title: str, department: str, experience: str,
                                qualifications: str, technical_skills: str,
                                soft_skills: str, responsibilities_input: str,
                                salary_range: str = "$90,000 - $130,000 USD") -> dict:
        """Generate structured job description with AI or intelligent synthesizer."""
        system_prompt = (
            "You are an expert Enterprise HR Talent Acquisition Specialist. "
            "Generate an articulate, comprehensive Job Description adhering to modern enterprise standards."
        )
        user_prompt = f"""
Job Title: {title}
Department: {department}
Experience: {experience}
Qualifications: {qualifications}
Technical Skills: {technical_skills}
Soft Skills: {soft_skills}
Key Responsibilities Input: {responsibilities_input}
Salary Range: {salary_range}

Please generate a professional JD with:
1. Overview
2. Key Responsibilities (4-6 detailed bullet points)
3. Required Qualifications
4. Technical Skills
5. Soft Skills
6. Company Expectations & Culture
7. Recommended Interview Questions (3 STAR questions)
8. Recommended Hiring Channels
"""
        generated_text = self.generate_text(system_prompt, user_prompt, temperature=0.5)

        # Structure the output
        overview = (
            f"We are seeking a talented and proactive {title} to join our {department} team at HR Nexus AI. "
            f"In this role, you will be instrumental in executing high-impact initiatives, driving operational excellence, "
            f"and collaborating with cross-functional partners to build cutting-edge systems."
        )

        resp_list = [
            f"Own the end-to-end design, execution, and optimization of {title} responsibilities.",
            "Collaborate closely with cross-departmental leads to align strategic milestones with business goals.",
            f"Implement industry standard best practices across {technical_skills.split(',')[0] if technical_skills else 'core tools'}.",
            "Identify operational bottlenecks, streamline manual workflows, and champion automated solutions.",
            "Participate actively in sprint ceremonies, sprint reviews, and retrospective planning."
        ]
        if responsibilities_input and len(responsibilities_input.strip()) > 10:
            resp_list.insert(0, responsibilities_input.strip())

        company_expectations = (
            "At HR Nexus AI, we foster an environment of high trust, continuous innovation, and psychological safety. "
            "We value clear communication, accountability, and the courage to propose transformative solutions. "
            "Employees receive competitive compensation, 20 days paid annual leave, comprehensive healthcare, and continuous learning stipends."
        )

        interview_questions = (
            f"1. STAR Question (Technical Mastery): Describe a situation where you had to master a new tool or framework ({technical_skills.split(',')[0] if technical_skills else 'core stack'}) quickly under a tight deadline. What was your approach and outcome?\n"
            f"2. STAR Question (Problem Solving): Can you share an example of a project where requirements changed midway? How did you adapt your plan and communicate with stakeholders?\n"
            f"3. Situational Question: How do you prioritize conflicting requests between speed-to-delivery and long-term quality?"
        )

        hiring_channels = "LinkedIn Recruiter, AngelList / Wellfound, Specialized Tech Community Slack/Discord, Referral Program, Glassdoor"

        return {
            "title": title,
            "department": department,
            "overview": overview,
            "responsibilities": "\n".join([f"• {r}" for r in resp_list]),
            "qualifications": qualifications or "Bachelor's or Master's degree in relevant field or equivalent practical experience.",
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "experience_requirements": experience,
            "salary_range": salary_range,
            "company_expectations": company_expectations,
            "interview_questions": interview_questions,
            "hiring_channels": hiring_channels,
            "raw_ai_output": generated_text
        }

    def save_jd(self, requisition_id: int, jd_data: dict) -> int:
        """Save generated JD to database."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO job_descriptions (
                    requisition_id, title, department, overview, responsibilities,
                    qualifications, technical_skills, soft_skills, experience_requirements,
                    salary_range, company_expectations, interview_questions, hiring_channels
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                requisition_id, jd_data['title'], jd_data['department'], jd_data['overview'],
                jd_data['responsibilities'], jd_data['qualifications'], jd_data['technical_skills'],
                jd_data['soft_skills'], jd_data['experience_requirements'], jd_data['salary_range'],
                jd_data['company_expectations'], jd_data['interview_questions'], jd_data['hiring_channels']
            ))
            return cursor.lastrowid

