"""
HR Nexus AI - 50 Candidates Seed Generator
Expands candidate repository to 50 comprehensive, realistic profiles across all 12 pipeline stages.
"""
from database.connection import get_db

CANDIDATES_50 = [
    # Format: (code, name, email, phone, location, education, exp, org, desig, notice, salary, req_id, stage, score, skills_match, exp_match, edu_match, rec)
    ("CAND-001", "Alex Rivera", "alex.rivera@example.com", "+1 555-0101", "Austin, TX", "B.S. Computer Science", 5.5, "Apex Cloud Inc.", "Senior Software Engineer", 30, 125000, 1, "Interview Completed", 93.3, 95.0, 90.0, 95.0, "Recommend for Offer"),
    ("CAND-002", "Priya Sharma", "priya.sharma@example.com", "+1 555-0102", "Seattle, WA", "M.S. Software Engineering", 6.0, "Nordic Systems", "Backend Python Developer", 15, 130000, 1, "Shortlisted", 94.0, 92.0, 95.0, 95.0, "Recommend for Interview"),
    ("CAND-003", "Marcus Brody", "marcus.brody@example.com", "+1 555-0103", "Chicago, IL", "B.S. Information Systems", 3.0, "Delta Corp", "Junior Python Developer", 30, 90000, 1, "Resume Screening", 70.0, 65.0, 60.0, 85.0, "Consider for Junior Role"),
    ("CAND-004", "Sophia Lin", "sophia.lin@example.com", "+1 555-0104", "San Francisco, CA", "M.S. Data Science", 4.5, "Insight Analytics", "Data Scientist", 45, 140000, 4, "Interview Scheduled", 92.7, 94.0, 88.0, 96.0, "Strong Recommend for Interview"),
    ("CAND-005", "Daniel O'Connor", "daniel.oc@example.com", "+1 555-0105", "Boston, MA", "Ph.D. Applied Math", 6.5, "AlphaBio Labs", "Lead ML Researcher", 60, 155000, 4, "Selected", 95.5, 96.0, 95.0, 96.0, "Strong Hire"),
    ("CAND-006", "Aisha Khan", "aisha.khan@example.com", "+1 555-0106", "New York, NY", "B.A. Human Resources", 3.5, "Vanguard People Co.", "HR Specialist", 30, 68000, 3, "Offer Accepted", 90.7, 92.0, 90.0, 90.0, "Hired / Onboarding Active"),
    ("CAND-007", "Carlos Mendez", "carlos.m@example.com", "+1 555-0107", "Miami, FL", "B.B.A. Management", 2.0, "Horizon Logistics", "HR Coordinator", 15, 58000, 3, "Applied", 68.0, 65.0, 60.0, 80.0, "Screening Pending"),
    ("CAND-008", "Emily Watson", "emily.watson@example.com", "+1 555-0108", "Denver, CO", "B.S. Economics & Business", 7.0, "KPMG Advisory", "Senior Business Consultant", 30, 110000, 2, "Offer Released", 94.3, 96.0, 95.0, 92.0, "Offer Dispatched"),
    ("CAND-009", "Rajesh Patel", "rajesh.patel@example.com", "+1 555-0109", "Atlanta, GA", "M.B.A. Information Systems", 5.0, "Equifax Systems", "Business Systems Analyst", 30, 102000, 2, "Shortlisted", 88.5, 90.0, 85.0, 90.0, "Recommend for Interview"),
    ("CAND-010", "Rachel Green", "rachel.green@example.com", "+1 555-0110", "New York, NY", "B.A. Fashion Merchandising", 1.0, "Ralph Lauren", "Retail Assistant", 15, 45000, 3, "Rejected", 45.0, 40.0, 30.0, 65.0, "Non-Matching Qualifications"),
    ("CAND-011", "Liam Neeson", "liam.n@example.com", "+1 555-0111", "Los Angeles, CA", "B.S. Computer Engineering", 8.0, "Skyline Security", "Principal Python Architect", 60, 150000, 1, "Talent Pool", 91.0, 92.0, 95.0, 85.0, "Retained for Future Lead Role"),
    ("CAND-012", "Fatima Al-Mansoor", "fatima.am@example.com", "+1 555-0112", "Dallas, TX", "M.S. Artificial Intelligence", 3.5, "Cognitive Solutions", "ML Engineer", 30, 125000, 4, "Assessment", 86.0, 88.0, 80.0, 90.0, "Assessment Under Review"),
    ("CAND-013", "Ethan Hunt", "ethan.hunt@example.com", "+1 555-0113", "Washington, DC", "B.S. Business Management", 4.0, "Mission Tech", "Business Analyst", 30, 88000, 2, "Applied", 75.0, 75.0, 75.0, 75.0, "Pending Detailed Screening"),
    ("CAND-014", "Zoe Saldana", "zoe.s@example.com", "+1 555-0114", "San Diego, CA", "B.S. Human Resources", 4.0, "Starlight Talent", "HR Generalist", 30, 70000, 3, "Shortlisted", 87.0, 88.0, 85.0, 88.0, "Recommend for HR Interview"),
    ("CAND-015", "Vikram Malhotra", "vikram.m@example.com", "+1 555-0115", "San Jose, CA", "B.Tech Computer Science", 5.0, "Wipro Digital", "Senior Python Engineer", 45, 128000, 1, "Assessment", 89.0, 90.0, 88.0, 89.0, "Coding Challenge in Progress"),
    ("CAND-016", "Chloe Bennett", "chloe.b@example.com", "+1 555-0116", "Portland, OR", "M.S. Human Capital", 3.0, "Nike Global", "Talent Acquisition Associate", 30, 65000, 3, "Interview Scheduled", 85.5, 86.0, 82.0, 89.0, "Round 1 Scheduled"),
    ("CAND-017", "Brian Miller", "brian.miller@example.com", "+1 555-0117", "Philadelphia, PA", "B.S. Statistics", 4.0, "Comcast Media", "Data Analyst", 30, 105000, 4, "Interview Completed", 84.0, 85.0, 80.0, 87.0, "Completed Panel Round"),
    ("CAND-018", "Grace Hopper", "grace.h@example.com", "+1 555-0118", "Arlington, VA", "Ph.D. Computer Science", 9.0, "Navy Cyber Command", "Lead Architect", 60, 160000, 1, "Selected", 98.0, 98.0, 98.0, 98.0, "Unanimous Selection"),
    ("CAND-019", "Lucas Silva", "lucas.silva@example.com", "+1 555-0119", "Raleigh, NC", "B.S. Computer Science", 4.5, "Red Hat", "Cloud Software Engineer", 30, 122000, 1, "Resume Screening", 83.0, 85.0, 80.0, 84.0, "Screening Passed"),
    ("CAND-020", "Hannah Abbott", "hannah.a@example.com", "+1 555-0120", "Salt Lake City, UT", "B.A. Organizational Psychology", 2.5, "Intermountain Health", "HR Assistant", 15, 54000, 3, "Applied", 71.0, 70.0, 65.0, 78.0, "Initial Application Received"),

    # Candidates 21-30
    ("CAND-021", "Nathan Drake", "nathan.drake@example.com", "+1 555-0121", "New York, NY", "B.S. Software Engineering", 6.0, "Naughty Cloud Corp", "Senior Backend Engineer", 30, 132000, 1, "Interview Completed", 91.5, 92.0, 90.0, 92.0, "Strong Technical Feedback"),
    ("CAND-022", "Elena Gilbert", "elena.g@example.com", "+1 555-0122", "San Francisco, CA", "M.B.A. Product Management", 5.5, "Mystic AI Labs", "AI Product Manager", 45, 145000, 5, "Interview Scheduled", 88.0, 90.0, 85.0, 89.0, "Product Discovery Round"),
    ("CAND-023", "Tariq Aziz", "tariq.aziz@example.com", "+1 555-0123", "Austin, TX", "B.Tech Information Tech", 5.0, "CloudShield Inc.", "DevOps Automation Engineer", 30, 126000, 1, "Shortlisted", 86.5, 88.0, 85.0, 86.0, "Recommend for Tech Screen"),
    ("CAND-024", "Maya Lin", "maya.lin@example.com", "+1 555-0124", "Seattle, WA", "M.S. Computational Linguistics", 4.0, "Amazon Alexa AI", "NLP Research Engineer", 30, 138000, 4, "Selected", 93.0, 95.0, 90.0, 94.0, "Top Tier NLP Specialist"),
    ("CAND-025", "Kevin Zhang", "kevin.zhang@example.com", "+1 555-0125", "Chicago, IL", "M.S. Computer Science", 7.0, "Citadel Securities", "Lead Python Engineer", 60, 152000, 1, "Offer Released", 95.0, 96.0, 95.0, 94.0, "Offer Extended"),
    ("CAND-026", "Samantha Reed", "samantha.r@example.com", "+1 555-0126", "Boston, MA", "M.S. Human Resource Management", 6.5, "HubSpot", "Senior HR Business Partner", 30, 95000, 3, "Selected", 92.0, 93.0, 90.0, 93.0, "Leadership Finalist"),
    ("CAND-027", "Oscar Isaac", "oscar.isaac@example.com", "+1 555-0127", "Denver, CO", "B.S. Business Information Systems", 5.0, "Palantir Tech", "Senior Systems Analyst", 30, 108000, 2, "Assessment", 85.0, 86.0, 84.0, 85.0, "Case Study Submitted"),
    ("CAND-028", "Nina Dobrev", "nina.dobrev@example.com", "+1 555-0128", "Atlanta, GA", "B.S. Industrial Engineering", 4.0, "The Home Depot Tech", "BI Systems Analyst", 30, 94000, 2, "Shortlisted", 83.5, 85.0, 80.0, 85.0, "Screening Confirmed"),
    ("CAND-029", "James Wilson", "james.wilson@example.com", "+1 555-0129", "San Diego, CA", "Ph.D. Statistics", 5.0, "Qualcomm AI", "Machine Learning Engineer", 45, 142000, 4, "Shortlisted", 90.0, 92.0, 88.0, 90.0, "Strong ML Candidate"),
    ("CAND-030", "Amara Okafor", "amara.okafor@example.com", "+1 555-0130", "Dallas, TX", "B.A. Communications & HR", 3.0, "AT&T Talent", "Talent Sourcing Specialist", 15, 66000, 3, "Interview Scheduled", 82.0, 84.0, 80.0, 82.0, "Behavioral Round 1"),

    # Candidates 31-40
    ("CAND-031", "Arthur Pendelton", "arthur.p@example.com", "+1 555-0131", "Miami, FL", "B.S. Computer Science", 5.0, "Royal Caribbean Tech", "Senior Backend Developer", 30, 118000, 1, "Resume Screening", 84.0, 85.0, 82.0, 85.0, "Strong FastAPI Background"),
    ("CAND-032", "Beatrice Vance", "beatrice.v@example.com", "+1 555-0132", "San Jose, CA", "M.B.A. Stanford", 8.0, "Cisco Systems", "Lead Product Manager", 60, 158000, 5, "Selected", 96.0, 96.0, 96.0, 96.0, "Exceptional Product Vision"),
    ("CAND-033", "Chen Wei", "chen.wei@example.com", "+1 555-0133", "Portland, OR", "M.S. Data Science", 5.0, "Intel Labs", "Senior Data Scientist", 30, 134000, 4, "Offer Accepted", 91.0, 92.0, 90.0, 91.0, "Onboarding Setup"),
    ("CAND-034", "Devendra Roy", "devendra.roy@example.com", "+1 555-0134", "Philadelphia, PA", "M.Tech Software Systems", 7.5, "SAP America", "Microservices Architect", 45, 148000, 1, "Hired", 97.0, 98.0, 96.0, 97.0, "Offer Accepted & Hired"),
    ("CAND-035", "Emma Stone", "emma.stone@example.com", "+1 555-0135", "New York, NY", "M.S. Human Resources", 5.0, "Bloomberg LP", "HR Operations Lead", 30, 88000, 3, "Offer Released", 93.0, 94.0, 92.0, 93.0, "Offer Under Review"),
    ("CAND-036", "Frank Castle", "frank.castle@example.com", "+1 555-0136", "Washington, DC", "B.S. Cybersecurity", 6.0, "Lockheed Martin", "Cloud Security Specialist", 30, 135000, 1, "Talent Pool", 88.0, 90.0, 86.0, 88.0, "Security SRE Talent Pool"),
    ("CAND-037", "Giselle Bundchen", "giselle.b@example.com", "+1 555-0137", "Los Angeles, CA", "M.B.A. Strategy", 6.0, "Deloitte Consulting", "Business Process Consultant", 30, 114000, 2, "Hired", 95.0, 96.0, 94.0, 95.0, "Hired for Enterprise Ops"),
    ("CAND-038", "Harry Osborn", "harry.osborn@example.com", "+1 555-0138", "Seattle, WA", "B.S. Computer Engineering", 4.0, "Oscorp Tech", "Fullstack Python Engineer", 30, 116000, 1, "Assessment", 81.0, 82.0, 80.0, 81.0, "Take-home API Assessment"),
    ("CAND-039", "Isabella Rossi", "isabella.r@example.com", "+1 555-0139", "Austin, TX", "Ph.D. Computer Vision", 4.5, "Tesla Autopilot", "AI/ML Specialist", 45, 146000, 4, "Interview Completed", 94.0, 95.0, 93.0, 94.0, "Panel Review Pending"),
    ("CAND-040", "Jamal Crawford", "jamal.c@example.com", "+1 555-0140", "Chicago, IL", "B.A. Psychology", 3.0, "Groupon", "Senior Talent Recruiter", 15, 68000, 3, "Interview Completed", 84.5, 85.0, 84.0, 84.0, "Culture Interview Done"),

    # Candidates 41-50
    ("CAND-041", "Kimberly Hart", "kimberly.h@example.com", "+1 555-0141", "Boston, MA", "B.S. Information Systems", 5.0, "Wayfair Engineering", "Senior Business Analyst", 30, 106000, 2, "Interview Completed", 89.0, 90.0, 88.0, 89.0, "Stakeholder Round Finished"),
    ("CAND-042", "Leo Valdez", "leo.valdez@example.com", "+1 555-0142", "Denver, CO", "B.S. Computer Science", 3.5, "Dish Network", "Backend API Developer", 30, 102000, 1, "Resume Screening", 79.0, 80.0, 78.0, 79.0, "Screening in Progress"),
    ("CAND-043", "Monica Geller", "monica.g@example.com", "+1 555-0143", "Atlanta, GA", "B.B.A. Human Resources", 4.0, "Delta Air Lines", "HR Compliance Specialist", 30, 76000, 3, "Shortlisted", 87.5, 88.0, 87.0, 87.0, "Shortlisted by HR"),
    ("CAND-044", "Neil Armstrong", "neil.a@example.com", "+1 555-0144", "San Francisco, CA", "Ph.D. Aeronautics & AI", 11.0, "NASA JPL / OpenAI", "Principal AI Research Scientist", 60, 185000, 4, "Hired", 99.0, 99.0, 99.0, 99.0, "Hired as Principal Scientist"),
    ("CAND-045", "Olivia Wilde", "olivia.wilde@example.com", "+1 555-0145", "San Jose, CA", "M.B.A. Haas School", 7.0, "Adobe Systems", "Product Strategy Lead", 45, 155000, 5, "Interview Completed", 92.5, 93.0, 92.0, 92.0, "Executive Interview Done"),
    ("CAND-046", "Peter Parker", "peter.parker@example.com", "+1 555-0146", "New York, NY", "B.S. Data Science", 2.0, "Daily Bugle Media", "Junior Data Scientist", 15, 88000, 4, "Resume Screening", 74.0, 75.0, 73.0, 74.0, "Under Review"),
    ("CAND-047", "Quinn Fabray", "quinn.f@example.com", "+1 555-0147", "Portland, OR", "B.A. Organizational Behavior", 3.5, "Columbia Sportswear", "People & Culture Generalist", 30, 69000, 3, "Assessment", 83.0, 84.0, 82.0, 83.0, "HR Scenario Test Active"),
    ("CAND-048", "Ravi Shankar", "ravi.shankar@example.com", "+1 555-0148", "Dallas, TX", "M.S. Computer Engineering", 6.5, "Texas Instruments", "Senior Distributed Systems Engineer", 30, 138000, 1, "Interview Scheduled", 93.5, 94.0, 93.0, 93.0, "Technical Round 2 Booked"),
    ("CAND-049", "Selena Gomez", "selena.g@example.com", "+1 555-0149", "Austin, TX", "B.S. Business Analytics", 4.0, "Dell Technologies", "Agile Business Analyst", 30, 98000, 2, "Resume Screening", 82.0, 83.0, 81.0, 82.0, "Requirements Evaluation"),
    ("CAND-050", "Tony Stark", "tony.stark@example.com", "+1 555-0150", "Los Angeles, CA", "Ph.D. Robotics & AI", 12.0, "Stark Industries", "Chief AI Architect", 60, 210000, 4, "Rejected", 60.0, 99.0, 99.0, 99.0, "Salary Expectation Beyond Range")
]

def seed_50_candidates():
    with get_db() as conn:
        cursor = conn.cursor()

        print("Seeding/updating 50 realistic candidate profiles across all 12 pipeline stages...")

        # Clear existing candidates and cascading records to provide clean seed
        cursor.execute("DELETE FROM screening_results;")
        cursor.execute("DELETE FROM applications;")
        cursor.execute("DELETE FROM candidate_skills;")
        cursor.execute("DELETE FROM resumes;")
        cursor.execute("DELETE FROM candidates;")

        for cand in CANDIDATES_50:
            (code, name, email, phone, loc, edu, exp, org, desig, notice, sal, req_id, stage, score, s_match, e_match, ed_match, rec) = cand

            # 1. Insert Candidate
            cursor.execute("""
                INSERT INTO candidates (
                    candidate_code, full_name, email, phone, location,
                    highest_education, total_experience_years, current_organization,
                    current_designation, notice_period_days, expected_salary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (code, name, email, phone, loc, edu, exp, org, desig, notice, sal))
            cand_id = cursor.lastrowid

            # 2. Insert Resume record
            cursor.execute("""
                INSERT INTO resumes (candidate_id, file_name, file_path, raw_text)
                VALUES (?, ?, ?, ?);
            """, (cand_id, f"{name.lower().replace(' ', '_')}_resume.pdf", f"/sample_resumes/{name.lower().replace(' ', '_')}_resume.pdf",
                  f"{name} | {email} | {phone} | {loc}\nExperience: {exp} years at {org} as {desig}.\nEducation: {edu}.\nSkills: Python, SQL, REST APIs, Git, Agile."))

            # 3. Insert Skills
            tech_skills = ["Python", "FastAPI", "SQL", "Docker", "Git"] if req_id == 1 else (
                ["Requirements Gathering", "BRD/FRD", "BPMN", "JIRA", "SQL"] if req_id == 2 else (
                    ["Recruitment", "HRMS", "Onboarding", "Statutory Compliance"] if req_id == 3 else (
                        ["Python", "PyTorch", "LLMs", "NLP", "Scikit-learn"] if req_id == 4 else
                        ["Product Discovery", "PRD Writing", "Roadmapping", "Metrics/KPIs"]
                    )
                )
            )
            for sk in tech_skills:
                cursor.execute("INSERT INTO candidate_skills (candidate_id, skill_name, skill_type) VALUES (?, ?, 'Technical');", (cand_id, sk))

            # 4. Insert Application
            app_code = f"APP-2026-{100 + cand_id}"
            cursor.execute("""
                INSERT INTO applications (
                    application_code, candidate_id, requisition_id, stage, source, status_notes, hr_manager_assigned
                ) VALUES (?, ?, ?, ?, 'Portal', ?, 'Sarah Jenkins');
            """, (app_code, cand_id, req_id, stage, f"Candidate in {stage} stage."))
            app_id = cursor.lastrowid

            # 5. Insert Screening Result
            cursor.execute("""
                INSERT INTO screening_results (
                    application_id, candidate_id, requisition_id,
                    skills_match_score, experience_match_score, education_match_score, overall_match_score,
                    matching_skills, missing_skills, candidate_summary, verification_flags,
                    recommendation, screening_rationale, human_reviewed, reviewed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'Sarah Jenkins');
            """, (
                app_id, cand_id, req_id,
                s_match, e_match, ed_match, score,
                ", ".join(tech_skills[:4]), "None noted",
                f"{name} is a {desig} with {exp} years of domain experience at {org}.",
                "Standard verification required",
                rec,
                f"Candidate achieved {score}% overall compatibility ({s_match}% skills, {e_match}% exp, {ed_match}% edu)."
            ))

        print(f"Successfully seeded {len(CANDIDATES_50)} candidates across all 12 pipeline stages!")

if __name__ == "__main__":
    seed_50_candidates()

