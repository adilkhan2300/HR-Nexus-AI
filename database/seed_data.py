"""
HR Nexus AI - Realistic Seed Data Generator
Pre-loads 5 jobs, 20 candidates, 10 interviews & feedback, 5 employees, 10 onboarding tasks,
5 detailed HR policies, users, and audit logs.
"""
import json
from datetime import datetime, timedelta
from database.connection import get_db, init_db

def seed_all_data():
    init_db()
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) as cnt FROM users;")
        if cursor.fetchone()["cnt"] > 0:
            print("Database already contains data. Skipping initial seeding.")
            return

        print("Seeding HR Nexus AI Database with comprehensive sample data...")

        # 1. Users
        users = [
            ("admin", "Adil Admin", "admin@hrnexus.ai", "admin123", "Admin", "Human Resources"),
            ("hrmanager", "Sarah Jenkins", "sarah.jenkins@hrnexus.ai", "hr123", "HR Manager", "Human Resources"),
            ("interviewer", "David Chen", "david.chen@hrnexus.ai", "tech123", "Interviewer / Dept Manager", "Engineering & Technology")
        ]
        cursor.executemany("""
            INSERT INTO users (username, full_name, email, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?, ?);
        """, users)

        # 2. Job Requisitions (5 realistic jobs)
        jobs = [
            (
                "REQ-2026-001", "Senior Python Developer", "Engineering & Technology", "Full-Time", 2,
                "4-7 Years", 95000, 135000, "USD", "David Chen", "High",
                "Bachelor's or Master's in Computer Science or related STEM field.",
                "Python, FastAPI, Django, PostgreSQL, Docker, Redis, REST APIs, Microservices, Unit Testing",
                "Agile collaboration, Technical mentorship, Problem solving, Clear architectural communication",
                "We are seeking an experienced Senior Python Developer to architect, build, and optimize scalable backend services and microservices powering our next-generation cloud platforms.",
                "Approved", "Adil Admin"
            ),
            (
                "REQ-2026-002", "Lead Business Analyst", "Operations & Legal", "Full-Time", 1,
                "5-8 Years", 85000, 115000, "USD", "Marcus Vance", "High",
                "Bachelor's in Business Administration, Information Systems, or Finance; CBAP certification preferred.",
                "Requirements Gathering, BRD/FRD Drafting, SQL, Process Mapping, BPMN, JIRA, Agile/Scrum",
                "Stakeholder management, Executive presentation, Analytical mindset, Cross-functional alignment",
                "Looking for a Lead Business Analyst to bridge the gap between business stakeholders and technical development squads.",
                "Approved", "Adil Admin"
            ),
            (
                "REQ-2026-003", "HR Executive - Talent & Operations", "Human Resources", "Full-Time", 1,
                "2-4 Years", 55000, 72000, "USD", "Sarah Jenkins", "Medium",
                "Bachelor's in Human Resource Management, Psychology, or Business.",
                "HRMS software, End-to-end recruitment, Candidate onboarding, Statutory compliance, Talent sourcing, Excel",
                "Empathy, Conflict resolution, Active listening, Discretion, Cultural evangelism",
                "Seeking an energetic HR Executive to drive end-to-end talent acquisition, seamless employee onboarding, and employee engagement initiatives.",
                "Approved", "Adil Admin"
            ),
            (
                "REQ-2026-004", "Data Scientist - AI / Machine Learning", "Engineering & Technology", "Full-Time", 2,
                "3-6 Years", 110000, 150000, "USD", "Elena Rostova", "Critical",
                "Master's or Ph.D. in Data Science, Computer Science, Statistics or Mathematics.",
                "Python, PyTorch, Scikit-learn, LLMs, NLP, Pandas, Feature Engineering, MLOps, SQL",
                "Experimental rigor, Scientific curiosity, Storytelling with data, Cross-team collaboration",
                "Drive production machine learning models and autonomous agent workflows to empower data-driven customer intelligence.",
                "Approved", "Adil Admin"
            ),
            (
                "REQ-2026-005", "Senior Product Manager", "Product & Design", "Full-Time", 1,
                "5-9 Years", 120000, 160000, "USD", "Marcus Vance", "Medium",
                "Bachelor's degree minimum, MBA or technical background preferred.",
                "Product discovery, Roadmapping, PRD writing, User research, Metrics/KPI tracking, A/B Testing, Mixpanel",
                "Product intuition, Decisiveness, Cross-functional leadership, Customer empathy",
                "Lead product strategy and execution for our core enterprise SaaS workflows from discovery to global launch.",
                "Pending", None
            )
        ]
        cursor.executemany("""
            INSERT INTO job_requisitions (
                requisition_code, title, department, employment_type, vacancies,
                experience_required, min_salary, max_salary, salary_currency, hiring_manager,
                priority, qualifications, technical_skills, soft_skills, job_description,
                approval_status, approved_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, jobs)

        # 3. Job Descriptions (Generated JD entries for approved requisitions)
        jds = [
            (
                1, "Senior Python Developer", "Engineering & Technology",
                "As a Senior Python Developer at HR Nexus Enterprises, you will design and implement resilient backend systems that handle millions of real-time transactions.",
                "Architect scalable microservices with FastAPI/Django; Optimize SQL query plans; Mentor junior developers; Participate in code reviews; Maintain 99.9% uptime SLA.",
                "B.S. or M.S. in Computer Science or equivalent practical experience.",
                "Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes, CI/CD",
                "Technical leadership, proactive ownership, strong debugging skills",
                "4-7 Years relevant engineering experience",
                "$95,000 - $135,000 USD Annual Base + Performance Bonus",
                "High standards of code craftsmanship, security-first mindset, collaborative communication.",
                "1. Explain how you would optimize a slow query in PostgreSQL with millions of records.\n2. How do you handle concurrency in Python?\n3. Describe a time you refactored a legacy service without downtime.",
                "LinkedIn Recruiter, GitHub Jobs, Hired.com, Tech Community Referrals"
            ),
            (
                2, "Lead Business Analyst", "Operations & Legal",
                "The Lead Business Analyst will orchestrate discovery workshops and translate complex business requirements into clear technical specifications.",
                "Facilitate stakeholder discovery sessions; Author exhaustive BRD and FRD documents; Conduct gap analysis; Define user acceptance criteria.",
                "Bachelor's in Business, IS, or CBAP Certified.",
                "Requirements Engineering, SQL, JIRA, BPMN 2.0, Tableau/PowerBI",
                "Negotiation, Conflict mediation, Executive presentation",
                "5-8 Years of business analysis experience in enterprise tech",
                "$85,000 - $115,000 USD Annual Base",
                "Commitment to clarity, zero ambiguity in functional specs, proactive partner to engineering.",
                "1. Walk us through your process for prioritizing conflicting stakeholder demands.\n2. How do you ensure user stories cover non-functional requirements?",
                "LinkedIn, Glassdoor, Industry Association Forums"
            )
        ]
        cursor.executemany("""
            INSERT INTO job_descriptions (
                requisition_id, title, department, overview, responsibilities,
                qualifications, technical_skills, soft_skills, experience_requirements,
                salary_range, company_expectations, interview_questions, hiring_channels
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, jds)

        # 4. Candidates (20 candidates)
        candidates_data = [
            ("CAND-001", "Alex Rivera", "alex.rivera@example.com", "+1 555-0101", "Austin, TX", "B.S. Computer Science", 5.5, "Apex Cloud Inc.", "Senior Software Engineer", 30, 125000),
            ("CAND-002", "Priya Sharma", "priya.sharma@example.com", "+1 555-0102", "Seattle, WA", "M.S. Software Engineering", 6.0, "Nordic Systems", "Backend Python Developer", 15, 130000),
            ("CAND-003", "Marcus Brody", "marcus.brody@example.com", "+1 555-0103", "Chicago, IL", "B.S. Information Systems", 3.0, "Delta Corp", "Junior Python Developer", 30, 90000),
            ("CAND-004", "Sophia Lin", "sophia.lin@example.com", "+1 555-0104", "San Francisco, CA", "M.S. Data Science", 4.5, "Insight Analytics", "Data Scientist", 45, 140000),
            ("CAND-005", "Daniel O'Connor", "daniel.oc@example.com", "+1 555-0105", "Boston, MA", "Ph.D. Applied Math", 6.5, "AlphaBio Labs", "Lead ML Researcher", 60, 155000),
            ("CAND-006", "Aisha Khan", "aisha.khan@example.com", "+1 555-0106", "New York, NY", "B.A. Human Resources", 3.5, "Vanguard People Co.", "HR Specialist", 30, 68000),
            ("CAND-007", "Carlos Mendez", "carlos.m@example.com", "+1 555-0107", "Miami, FL", "B.B.A. Management", 2.0, "Horizon Logistics", "HR Coordinator", 15, 58000),
            ("CAND-008", "Emily Watson", "emily.watson@example.com", "+1 555-0108", "Denver, CO", "B.S. Economics & Business", 7.0, "KPMG Advisory", "Senior Business Consultant", 30, 110000),
            ("CAND-009", "Rajesh Patel", "rajesh.patel@example.com", "+1 555-0109", "Atlanta, GA", "M.B.A. Information Systems", 5.0, "Equifax Systems", "Business Systems Analyst", 30, 102000),
            ("CAND-010", "Rachel Green", "rachel.green@example.com", "+1 555-0110", "New York, NY", "B.A. Fashion Merchandising", 1.0, "Ralph Lauren", "Retail Assistant", 15, 45000),
            ("CAND-011", "Liam Neeson", "liam.n@example.com", "+1 555-0111", "Los Angeles, CA", "B.S. Computer Engineering", 8.0, "Skyline Security", "Principal Python Architect", 60, 150000),
            ("CAND-012", "Fatima Al-Mansoor", "fatima.am@example.com", "+1 555-0112", "Dallas, TX", "M.S. Artificial Intelligence", 3.5, "Cognitive Solutions", "ML Engineer", 30, 125000),
            ("CAND-013", "Ethan Hunt", "ethan.hunt@example.com", "+1 555-0113", "Washington, DC", "B.S. Business Management", 4.0, "Mission Tech", "Business Analyst", 30, 88000),
            ("CAND-014", "Zoe Saldana", "zoe.s@example.com", "+1 555-0114", "San Diego, CA", "B.S. Human Resources", 4.0, "Starlight Talent", "HR Generalist", 30, 70000),
            ("CAND-015", "Vikram Malhotra", "vikram.m@example.com", "+1 555-0115", "San Jose, CA", "B.Tech Computer Science", 5.0, "Wipro Digital", "Senior Python Engineer", 45, 128000),
            ("CAND-016", "Chloe Bennett", "chloe.b@example.com", "+1 555-0116", "Portland, OR", "M.S. Human Capital", 3.0, "Nike Global", "Talent Acquisition Associate", 30, 65000),
            ("CAND-017", "Brian Miller", "brian.miller@example.com", "+1 555-0117", "Philadelphia, PA", "B.S. Statistics", 4.0, "Comcast Media", "Data Analyst", 30, 105000),
            ("CAND-018", "Grace Hopper", "grace.h@example.com", "+1 555-0118", "Arlington, VA", "Ph.D. Computer Science", 9.0, "Navy Cyber Command", "Lead Architect", 60, 160000),
            ("CAND-019", "Lucas Silva", "lucas.silva@example.com", "+1 555-0119", "Raleigh, NC", "B.S. Computer Science", 4.5, "Red Hat", "Cloud Software Engineer", 30, 122000),
            ("CAND-020", "Hannah Abbott", "hannah.a@example.com", "+1 555-0120", "Salt Lake City, UT", "B.A. Organizational Psychology", 2.5, "Intermountain Health", "HR Assistant", 15, 54000)
        ]
        cursor.executemany("""
            INSERT INTO candidates (
                candidate_code, full_name, email, phone, location,
                highest_education, total_experience_years, current_organization,
                current_designation, notice_period_days, expected_salary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, candidates_data)

        # 5. Resumes Text for candidate profiles
        resumes = [
            (
                1, "alex_rivera_resume.pdf", "/sample_resumes/alex_rivera_resume.pdf",
                """ALEX RIVERA | Austin, TX | alex.rivera@example.com | +1 555-0101
SUMMARY: Senior Software Engineer with 5.5 years of experience building resilient microservices using Python, FastAPI, Django, Docker, and PostgreSQL.
EXPERIENCE:
- Senior Software Engineer, Apex Cloud Inc. (2022 - Present): Led migration of monolithic monolith into 8 containerized microservices using FastAPI and Docker. Managed Redis caching reducing query response time by 42%.
- Software Engineer, NovaTech (2019 - 2022): Developed REST APIs with Django and PostgreSQL. Configured CI/CD GitHub Actions pipelines.
EDUCATION: B.S. in Computer Science, University of Texas at Austin (2015 - 2019).
SKILLS: Python, FastAPI, Django, PostgreSQL, Docker, Redis, REST APIs, Git, Kubernetes, Unit Testing.
CERTIFICATIONS: AWS Certified Developer Associate (2023)."""
            ),
            (
                2, "priya_sharma_resume.pdf", "/sample_resumes/priya_sharma_resume.pdf",
                """PRIYA SHARMA | Seattle, WA | priya.sharma@example.com | +1 555-0102
SUMMARY: Backend Python Engineer with 6.0 years of experience in distributed systems, microservices, and high-performance databases.
EXPERIENCE:
- Backend Python Developer, Nordic Systems (2021 - Present): Designed multi-tenant REST APIs using Python, FastAPI, and SQLAlchemy. Maintained PostgreSQL clusters and Redis queues.
- Software Engineer, Infosys (2018 - 2021): Built enterprise services with Python and Flask.
EDUCATION: M.S. in Software Engineering, University of Washington (2016 - 2018).
SKILLS: Python, FastAPI, Flask, PostgreSQL, Docker, Microservices, Redis, Git, Unit Testing.
CERTIFICATIONS: Docker Certified Associate."""
            ),
            (
                4, "sophia_lin_resume.pdf", "/sample_resumes/sophia_lin_resume.pdf",
                """SOPHIA LIN | San Francisco, CA | sophia.lin@example.com | +1 555-0104
SUMMARY: Data Scientist & ML Engineer with 4.5 years of industry experience deploying NLP pipelines, predictive models, and LLM applications.
EXPERIENCE:
- Data Scientist, Insight Analytics (2022 - Present): Fine-tuned open-source LLMs using PyTorch and HuggingFace for enterprise customer sentiment analysis. Deployed inference pipelines on AWS.
- Junior Data Scientist, DataCorp (2020 - 2022): Developed scikit-learn models for churn prediction and customer segmentation.
EDUCATION: M.S. in Data Science, UC Berkeley (2018 - 2020).
SKILLS: Python, PyTorch, Scikit-learn, LLMs, NLP, Pandas, NumPy, SQL, Feature Engineering, Docker.
CERTIFICATIONS: TensorFlow Developer Certificate."""
            ),
            (
                6, "aisha_khan_resume.pdf", "/sample_resumes/aisha_khan_resume.pdf",
                """AISHA KHAN | New York, NY | aisha.khan@example.com | +1 555-0106
SUMMARY: People & Talent Specialist with 3.5 years of experience in end-to-end recruitment, onboarding workflows, employee engagement, and HR compliance.
EXPERIENCE:
- HR Specialist, Vanguard People Co. (2022 - Present): Streamlined recruitment lifecycles for 60+ technical and operational hires annually. Implemented structured 30-day onboarding checklists.
- HR Associate, TalentBridge (2021 - 2022): Managed candidate pipelines in BambooHR and Workday. Facilitated new hire orientation sessions.
EDUCATION: B.A. in Human Resources Management, NYU (2017 - 2021).
SKILLS: End-to-end recruitment, HRMS, Onboarding, Talent Sourcing, Statutory Compliance, Excel, Candidate Experience.
CERTIFICATIONS: SHRM-CP (2023)."""
            ),
            (
                8, "emily_watson_resume.pdf", "/sample_resumes/emily_watson_resume.pdf",
                """EMILY WATSON | Denver, CO | emily.watson@example.com | +1 555-0108
SUMMARY: Lead Business Analyst with 7 years of enterprise consulting experience translating multi-million dollar business objectives into clear BRDs and technical requirements.
EXPERIENCE:
- Senior Business Consultant, KPMG Advisory (2021 - Present): Led business requirements gathering workshops with C-level executives. Defined BPMN workflows and managed JIRA backlogs.
- Business Analyst, Accenture (2017 - 2021): Documented FRDs, mapped as-is vs to-be architectures, and authored SQL validation queries.
EDUCATION: B.S. in Economics & Business, Colorado State University (2013 - 2017).
SKILLS: Requirements Gathering, BRD/FRD Drafting, SQL, Process Mapping, BPMN, JIRA, Agile/Scrum, Tableau.
CERTIFICATIONS: CBAP (Certified Business Analysis Professional)."""
            )
        ]
        cursor.executemany("""
            INSERT INTO resumes (candidate_id, file_name, file_path, raw_text)
            VALUES (?, ?, ?, ?);
        """, resumes)

        # 6. Candidate Skills
        skills_data = [
            (1, "Python", "Technical", "Expert", 1),
            (1, "FastAPI", "Technical", "Expert", 1),
            (1, "Docker", "Technical", "Intermediate", 1),
            (1, "PostgreSQL", "Technical", "Expert", 1),
            (1, "Redis", "Technical", "Intermediate", 1),
            (2, "Python", "Technical", "Expert", 1),
            (2, "FastAPI", "Technical", "Expert", 1),
            (2, "Microservices", "Technical", "Expert", 1),
            (4, "Python", "Technical", "Expert", 1),
            (4, "PyTorch", "Technical", "Expert", 1),
            (4, "LLMs", "Technical", "Advanced", 1),
            (6, "Recruitment", "Domain", "Expert", 1),
            (6, "Onboarding", "Domain", "Expert", 1),
            (6, "HRMS", "Tool", "Advanced", 1),
            (8, "BRD/FRD Drafting", "Domain", "Expert", 1),
            (8, "SQL", "Technical", "Advanced", 1),
            (8, "BPMN", "Domain", "Expert", 1)
        ]
        cursor.executemany("""
            INSERT INTO candidate_skills (candidate_id, skill_name, skill_type, proficiency_level, verified)
            VALUES (?, ?, ?, ?, ?);
        """, skills_data)

        # 7. Applications (Across multiple pipeline stages)
        applications_data = [
            ("APP-2026-001", 1, 1, "Interview Completed", "LinkedIn", "2026-03-01 10:00:00", "Top candidate for Senior Python role; completed Round 2.", "Sarah Jenkins"),
            ("APP-2026-002", 2, 1, "Shortlisted", "Referral", "2026-03-02 11:30:00", "Strong backend architecture skills.", "Sarah Jenkins"),
            ("APP-2026-003", 3, 1, "Resume Screening", "Career Portal", "2026-03-04 09:15:00", "Under experience requirement by 1 year.", "Sarah Jenkins"),
            ("APP-2026-004", 4, 4, "Interview Scheduled", "GitHub Jobs", "2026-03-01 14:00:00", "Strong NLP and LLM project portfolio.", "Sarah Jenkins"),
            ("APP-2026-005", 5, 4, "Selected", "Direct Outreach", "2026-02-25 16:00:00", "Offer ready to be drafted; approved by Elena.", "Sarah Jenkins"),
            ("APP-2026-006", 6, 3, "Offer Accepted", "LinkedIn", "2026-02-20 10:00:00", "Candidate accepted offer; onboarding initiated.", "Sarah Jenkins"),
            ("APP-2026-007", 7, 3, "Applied", "Portal", "2026-03-05 13:00:00", "New application received today.", "Sarah Jenkins"),
            ("APP-2026-008", 8, 2, "Offer Released", "Referral", "2026-02-26 15:30:00", "Offer letter sent; awaiting signature.", "Sarah Jenkins"),
            ("APP-2026-009", 9, 2, "Shortlisted", "Portal", "2026-03-02 08:45:00", "Passed initial screening.", "Sarah Jenkins"),
            ("APP-2026-010", 10, 3, "Rejected", "Portal", "2026-03-03 12:00:00", "Does not meet basic HRMS and compliance requirements.", "Sarah Jenkins"),
            ("APP-2026-011", 11, 1, "Talent Pool", "LinkedIn", "2026-02-15 11:00:00", "Very senior, keep in pipeline for Staff Engineer.", "Sarah Jenkins"),
            ("APP-2026-012", 12, 4, "Assessment", "Portal", "2026-03-03 14:30:00", "Take-home ML test sent.", "Sarah Jenkins"),
            ("APP-2026-013", 13, 2, "Applied", "Glassdoor", "2026-03-04 10:00:00", "Pending initial screening.", "Sarah Jenkins"),
            ("APP-2026-014", 14, 3, "Shortlisted", "LinkedIn", "2026-03-02 16:00:00", "Scheduled for phone screen.", "Sarah Jenkins"),
            ("APP-2026-015", 15, 1, "Assessment", "Portal", "2026-03-01 17:00:00", "Coding challenge in progress.", "Sarah Jenkins")
        ]
        cursor.executemany("""
            INSERT INTO applications (
                application_code, candidate_id, requisition_id, stage,
                source, applied_date, status_notes, hr_manager_assigned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, applications_data)

        # 8. Screening Results (Explainable AI scores)
        screenings = [
            (
                1, 1, 1, 95.0, 90.0, 95.0, 93.3,
                "Python, FastAPI, Django, PostgreSQL, Docker, Redis, Unit Testing",
                "Kubernetes production scale",
                "Alex exceeds technical qualifications with 5.5 years of specialized Python/FastAPI backend engineering. Proven experience reducing query latencies.",
                "Verify AWS certification credential ID; confirm notice period duration.",
                "Recommend for Interview",
                "Strong match across all primary skills (FastAPI, PostgreSQL, Microservices). Meets educational and 4-7 year experience threshold exactly.",
                1, "Sarah Jenkins"
            ),
            (
                2, 2, 1, 92.0, 95.0, 95.0, 94.0,
                "Python, FastAPI, PostgreSQL, Docker, Microservices, Redis",
                "Django framework deep exposure",
                "Priya brings 6.0 years of robust backend distributed systems experience. Strong academic foundation with M.S. Software Engineering.",
                "None noted; credentials well verified.",
                "Recommend for Interview",
                "High match in Python microservices and database tuning.",
                1, "Sarah Jenkins"
            ),
            (
                3, 3, 1, 65.0, 60.0, 85.0, 70.0,
                "Python, REST APIs, Git",
                "FastAPI, Docker, Microservices, Distributed Systems",
                "Candidate has 3 years total experience, falling slightly short of the 4-7 years requirement.",
                "Experience duration requires confirmation.",
                "Consider for Junior Role / Hold",
                "Good fundamentals in Python but lacks enterprise architectural microservices depth.",
                1, "Sarah Jenkins"
            ),
            (
                4, 4, 4, 94.0, 88.0, 96.0, 92.7,
                "Python, PyTorch, Scikit-learn, LLMs, NLP, SQL",
                "MLOps deployment at scale",
                "Sophia has excellent academic credentials (M.S. UC Berkeley) and direct hands-on experience fine-tuning LLMs with PyTorch.",
                "Verify publication claims.",
                "Strong Recommend for Interview",
                "Direct alignment with AI Agent and NLP strategic initiatives.",
                1, "Sarah Jenkins"
            ),
            (
                6, 6, 3, 92.0, 90.0, 90.0, 90.7,
                "End-to-end recruitment, HRMS, Onboarding, Compliance",
                "Global payroll administration",
                "Aisha has 3.5 years of targeted talent acquisition and onboarding experience with SHRM-CP certification.",
                "SHRM-CP verified.",
                "Recommend for Selection",
                "Solid culture fit and demonstrated ability to handle onboarding workflows smoothly.",
                1, "Sarah Jenkins"
            ),
            (
                8, 8, 2, 96.0, 95.0, 92.0, 94.3,
                "Requirements Gathering, BRD/FRD, SQL, BPMN, JIRA, Agile",
                "Python data analysis scripting",
                "Outstanding consulting profile with CBAP certification and 7 years of deep enterprise analysis experience at KPMG.",
                "None.",
                "Recommend for Offer",
                "Exceeds role requirements. Excellent communication and documentation capabilities.",
                1, "Marcus Vance"
            )
        ]
        cursor.executemany("""
            INSERT INTO screening_results (
                application_id, candidate_id, requisition_id,
                skills_match_score, experience_match_score, education_match_score, overall_match_score,
                matching_skills, missing_skills, candidate_summary, verification_flags,
                recommendation, screening_rationale, human_reviewed, reviewed_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, screenings)

        # 9. Interviews (10 records)
        interviews_data = [
            ("INT-001", 1, 1, 1, "Technical Round 1", 1, "David Chen", "david.chen@hrnexus.ai", "2026-03-03 14:00:00", 60, "https://meet.google.com/abc-defg-hij", "Completed", 1),
            ("INT-002", 1, 1, 1, "System Architecture Round 2", 2, "David Chen", "david.chen@hrnexus.ai", "2026-03-05 11:00:00", 60, "https://meet.google.com/klm-nopq-rst", "Completed", 1),
            ("INT-003", 2, 2, 1, "Technical Round 1", 1, "David Chen", "david.chen@hrnexus.ai", "2026-03-08 15:00:00", 60, "https://meet.google.com/uvw-xyza-bcd", "Scheduled", 1),
            ("INT-004", 4, 4, 4, "ML Deep Dive Round 1", 1, "Elena Rostova", "elena.r@hrnexus.ai", "2026-03-07 10:00:00", 60, "https://meet.google.com/efg-hijk-lmn", "Scheduled", 1),
            ("INT-005", 5, 5, 4, "Executive Round 2", 2, "Elena Rostova", "elena.r@hrnexus.ai", "2026-03-02 16:00:00", 45, "https://meet.google.com/opq-rstu-vwx", "Completed", 1),
            ("INT-006", 6, 6, 3, "HR Management Round 1", 1, "Sarah Jenkins", "sarah.jenkins@hrnexus.ai", "2026-02-22 11:00:00", 45, "https://meet.google.com/yza-bcde-fgh", "Completed", 1),
            ("INT-007", 6, 6, 3, "Culture & Fit Round 2", 2, "Adil Admin", "admin@hrnexus.ai", "2026-02-24 14:00:00", 45, "https://meet.google.com/ijk-lmno-pqr", "Completed", 1),
            ("INT-008", 8, 8, 2, "Case Study Round 1", 1, "Marcus Vance", "marcus.v@hrnexus.ai", "2026-02-23 10:00:00", 60, "https://meet.google.com/stu-vwxy-zab", "Completed", 1),
            ("INT-009", 8, 8, 2, "Stakeholder Management Round 2", 2, "Marcus Vance", "marcus.v@hrnexus.ai", "2026-02-25 13:00:00", 45, "https://meet.google.com/cde-fghi-jkl", "Completed", 1),
            ("INT-010", 9, 9, 2, "Technical Screening Round 1", 1, "Marcus Vance", "marcus.v@hrnexus.ai", "2026-03-09 11:30:00", 45, "https://meet.google.com/mno-pqrs-tuv", "Scheduled", 0)
        ]
        cursor.executemany("""
            INSERT INTO interviews (
                interview_code, application_id, candidate_id, requisition_id,
                round_name, round_number, interviewer_name, interviewer_email,
                scheduled_time, duration_minutes, meeting_link, status, attendance_confirmed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, interviews_data)

        # 10. Interview Feedback
        feedback_data = [
            (
                1, "David Chen", 9.2, 8.5, 9.0, 9.0, 9.0, 8.9,
                "Flawless understanding of Python GIL, asynchronous I/O, and PostgreSQL indexing strategies.",
                "Minor rustiness on Kubernetes custom resource definitions.",
                "Alex solved the distributed caching concurrency problem with remarkable elegance. Would be an immediate asset to our backend squad.",
                "Strong Hire"
            ),
            (
                2, "David Chen", 9.5, 8.8, 9.2, 9.0, 9.5, 9.2,
                "Strong architectural thinking; drafted clear zero-downtime database migration schema live.",
                "None of note.",
                "Exceeded expectations in system architecture. Highly recommend extending offer.",
                "Strong Hire"
            ),
            (
                5, "Elena Rostova", 9.0, 9.0, 9.5, 9.0, 9.5, 9.2,
                "Exceptional mathematical foundation and deep intuition for LLM attention mechanics.",
                "Prefers research over fast-paced sprint delivery.",
                "Dr. O'Connor is world-class in generative models and AI agent algorithms.",
                "Strong Hire"
            ),
            (
                6, "Sarah Jenkins", 8.8, 9.5, 8.5, 9.2, 8.8, 8.9,
                "Great communicator, understands employment statutory guidelines and onboarding friction points.",
                "Needs slight mentoring on international visa compliance.",
                "Very cheerful, proactive mindset. Will fit our company culture seamlessly.",
                "Hire"
            ),
            (
                8, "Marcus Vance", 9.5, 9.8, 9.2, 9.5, 9.5, 9.5,
                "Superb presentation skills. Handled scope change curveballs in the case study with extreme composure.",
                "None.",
                "Top tier candidate for Lead BA. Must hire immediately.",
                "Strong Hire"
            )
        ]
        cursor.executemany("""
            INSERT INTO interview_feedback (
                interview_id, interviewer_name, technical_score, communication_score,
                problem_solving_score, competency_score, experience_score, overall_rating,
                strengths, weaknesses, detailed_comments, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, feedback_data)

        # 11. Communications (Email logs)
        comms = [
            (
                1, 1, "Interview Invitation", "Invitation to Interview: Senior Python Developer at HR Nexus AI",
                "Dear Alex,\n\nWe were impressed by your background in Python backend engineering and would like to invite you for a 60-minute Technical Round with David Chen.\n\nDate: March 3, 2026\nTime: 2:00 PM EST\nMeeting Link: https://meet.google.com/abc-defg-hij\n\nBest regards,\nSarah Jenkins\nHR Nexus AI Team",
                "sarah.jenkins@hrnexus.ai", "alex.rivera@example.com", "Sent", 0, "Sarah Jenkins", "2026-03-01 11:00:00"
            ),
            (
                6, 6, "Offer Letter Communication", "Official Offer of Employment - HR Executive at HR Nexus AI",
                "Dear Aisha,\n\nWe are delighted to extend you an official offer to join HR Nexus AI as HR Executive - Talent & Operations. Your proposed annual compensation is $68,000 USD.\n\nPlease find your formal offer letter attached for review.\n\nWarm regards,\nSarah Jenkins",
                "sarah.jenkins@hrnexus.ai", "aisha.khan@example.com", "Sent", 1, "Sarah Jenkins", "2026-02-25 15:00:00"
            ),
            (
                8, 8, "Offer Letter Communication", "Offer Letter: Lead Business Analyst at HR Nexus AI",
                "Dear Emily,\n\nCongratulations! We are thrilled to offer you the position of Lead Business Analyst at HR Nexus AI with an annual CTC of $110,000 USD.\n\nWarm regards,\nAdil Admin",
                "admin@hrnexus.ai", "emily.watson@example.com", "Sent", 1, "Adil Admin", "2026-02-26 16:00:00"
            )
        ]
        cursor.executemany("""
            INSERT INTO communications (
                candidate_id, application_id, communication_type, subject,
                body_text, sender, recipient_email, status, approval_required,
                approved_by, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, comms)

        # 12. Offers
        offers_data = [
            (
                "OFF-2026-001", 6, 6, 3, "HR Executive - Talent & Operations", "Human Resources",
                "Sarah Jenkins", "2026-03-15", 68000, "USD", "New York, NY (Hybrid)", "Full-Time",
                "Standard 90-day probationary period. Health, dental, vision insurance coverage effective day one. 20 days paid annual leave.",
                "Accepted", "Sarah Jenkins", "2026-02-25 14:00:00"
            ),
            (
                "OFF-2026-002", 8, 8, 2, "Lead Business Analyst", "Operations & Legal",
                "Marcus Vance", "2026-04-01", 110000, "USD", "Denver, CO (Remote)", "Full-Time",
                "Standard non-disclosure, IP assignment, and 90-day probation terms apply.",
                "Released", "Adil Admin", "2026-02-26 15:30:00"
            ),
            (
                "OFF-2026-003", 5, 5, 4, "Lead ML Researcher", "Engineering & Technology",
                "Elena Rostova", "2026-04-15", 155000, "USD", "Boston, MA (Hybrid)", "Full-Time",
                "Annual equity grant, comprehensive benefits, publication sponsorship.",
                "Approved by HR", "Adil Admin", "2026-03-03 10:00:00"
            )
        ]
        cursor.executemany("""
            INSERT INTO offers (
                offer_code, application_id, candidate_id, requisition_id,
                designation, department, reporting_manager, joining_date,
                annual_ctc, currency, work_location, employment_type,
                terms_and_conditions, offer_status, hr_approved_by, approved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, offers_data)

        # 13. Employees (5 realistic employees)
        employees_data = [
            ("EMP-2026-001", "Aisha Khan", "aisha.khan@hrnexus.ai", "+1 555-0106", "Human Resources", "HR Executive", "Sarah Jenkins", "2026-03-15", "New York, NY", "Full-Time", "Probation", 65, "Partial"),
            ("EMP-2025-089", "Robert King", "robert.king@hrnexus.ai", "+1 555-0189", "Engineering & Technology", "Staff Backend Engineer", "David Chen", "2025-06-01", "Austin, TX", "Full-Time", "Active", 100, "Verified"),
            ("EMP-2025-092", "Claire Dupont", "claire.dupont@hrnexus.ai", "+1 555-0192", "Product & Design", "Senior Product Designer", "Marcus Vance", "2025-08-15", "San Francisco, CA", "Full-Time", "Active", 100, "Verified"),
            ("EMP-2025-104", "Tariq Mansoor", "tariq.mansoor@hrnexus.ai", "+1 555-0195", "Sales & Marketing", "Account Executive", "Sarah Jenkins", "2025-11-01", "Chicago, IL", "Full-Time", "Confirmed", 100, "Verified"),
            ("EMP-2026-002", "Jason Wu", "jason.wu@hrnexus.ai", "+1 555-0199", "Engineering & Technology", "DevOps Engineer", "David Chen", "2026-02-01", "Seattle, WA", "Full-Time", "Probation", 85, "Verified")
        ]
        cursor.executemany("""
            INSERT INTO employees (
                employee_code, full_name, email, personal_phone,
                department, designation, reporting_manager, joining_date,
                work_location, employment_type, employment_status,
                onboarding_progress, doc_verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, employees_data)

        # 14. Employee Documents (for Aisha Khan EMP-2026-001)
        docs = [
            (1, "Identity Proof", "passport_scan_ak.pdf", "/uploads/passport_scan_ak.pdf", "Verified", "Valid passport verified.", "Sarah Jenkins", "2026-03-01"),
            (1, "Address Proof", "utility_bill_ak.pdf", "/uploads/utility_bill_ak.pdf", "Verified", "Utility bill verified.", "Sarah Jenkins", "2026-03-01"),
            (1, "Educational Certificates", "degree_certificate_ak.pdf", "/uploads/degree_certificate_ak.pdf", "Under Verification", "Awaiting university transcript validation.", None, None),
            (1, "Previous Employment Release", "relieving_letter_vanguard.pdf", "/uploads/relieving_letter_vanguard.pdf", "Submitted", "Submitted by candidate.", None, None),
            (1, "Bank & Statutory Details", "void_check_ak.pdf", "/uploads/void_check_ak.pdf", "Pending", "Direct deposit form pending upload.", None, None)
        ]
        cursor.executemany("""
            INSERT INTO employee_documents (
                employee_id, document_type, document_name, file_path,
                status, verification_notes, verified_by, verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, docs)

        # 15. Onboarding Tasks (10 realistic tasks across 4 phases)
        tasks = [
            (1, "Pre-Joining", "Submit signed offer letter & tax declarations", "Candidate must sign employment agreement and submit W-4/tax forms.", "Aisha Khan", "2026-03-10", "Completed", "2026-03-02", "Aisha Khan"),
            (1, "Pre-Joining", "Upload educational and previous employment proofs", "Provide degree certificate and prior employment relieving letter.", "Aisha Khan", "2026-03-12", "In Progress", None, None),
            (1, "Day 1", "IT Equipment and Access Provisioning", "Ship MacBook Pro, setup corporate Google Workspace, Slack, and VPN.", "David Chen", "2026-03-15", "Pending", None, None),
            (1, "Day 1", "HR Welcome Orientation & Policy Briefing", "Conduct 60-min orientation on company culture, leave policy, and benefits.", "Sarah Jenkins", "2026-03-15", "Pending", None, None),
            (1, "Day 1", "Employee ID & Security Badge Generation", "Generate physical badge and issue virtual security token.", "Sarah Jenkins", "2026-03-15", "Pending", None, None),
            (1, "First Week", "Department Intro & Team Welcome Lunch", "Introduce to HR and talent operations squad.", "Sarah Jenkins", "2026-03-19", "Pending", None, None),
            (1, "First Week", "Standard Operating Procedures (SOP) Walkthrough", "Review recruitment compliance and ATS workflow guidelines.", "Sarah Jenkins", "2026-03-20", "Pending", None, None),
            (1, "First Week", "System Access to HRMS & BambooHR", "Grant administrative permissions to candidate database.", "David Chen", "2026-03-18", "Pending", None, None),
            (1, "First 30 Days", "30-Day Check-in & Goal Alignment", "Review initial progress on talent sourcing KPIs and address questions.", "Sarah Jenkins", "2026-04-14", "Pending", None, None),
            (1, "First 30 Days", "Probation Milestone Evaluation", "Evaluate initial 30 days performance and provide structured feedback.", "Sarah Jenkins", "2026-04-15", "Pending", None, None)
        ]
        cursor.executemany("""
            INSERT INTO onboarding_tasks (
                employee_id, phase, task_title, task_description,
                assigned_to, due_date, status, completed_at, completed_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, tasks)

        # 16. HR Policies (5 detailed policy documents for RAG)
        policies = [
            (
                "Company Leave Policy", "Leave & Attendance", "3.2",
                """HR NEXUS ENTERPRISES - COMPREHENSIVE LEAVE POLICY
1. Annual Leave (Paid Time Off):
All full-time employees accrue 20 days of paid annual leave per calendar year, accrued monthly at 1.67 days per month. Unused annual leave up to a maximum of 5 days may be carried over to the subsequent calendar year, expiring on March 31st.

2. Sick & Medical Leave:
Employees are entitled to 10 days of paid sick leave annually. For consecutive absences of 3 or more business days, a verified medical certificate from a licensed practitioner must be uploaded to the HRMS within 48 hours of return.

3. Parental Leave:
Primary caregivers are eligible for 16 consecutive weeks of fully paid parental leave. Secondary caregivers receive 6 consecutive weeks of fully paid leave. Employees must have completed at least 6 months of continuous service to qualify.

4. Bereavement Leave:
Employees may avail up to 5 consecutive paid days off for the loss of an immediate family member (spouse, child, parent, sibling).

5. Leave Application Workflow:
All leave requests must be submitted via the HRMS at least 5 business days in advance for planned vacations. Department managers hold approval authority. Emergency sick leaves should be notified via Slack or email by 9:00 AM on the day of absence.""",
                "Outlines PTO (20 days), Sick leave (10 days), Parental leave (16 weeks primary, 6 weeks secondary), and application timelines.",
                "2026-01-01"
            ),
            (
                "Code of Conduct and Ethical Business Practice", "Ethics & Governance", "2.0",
                """HR NEXUS ENTERPRISES - CODE OF CONDUCT
1. Workplace Dignity and Anti-Harassment:
HR Nexus is committed to providing an inclusive, harassment-free workplace. Discrimination or harassment on the basis of race, gender, religion, sexual orientation, disability, or marital status is strictly prohibited with zero tolerance.

2. Conflict of Interest:
Employees must avoid outside business activities, investments, or consultancies that conflict with company interests. Any dual employment or moonlighting requires written pre-approval from the Chief People Officer and Legal.

3. Data Confidentiality and Intellectual Property:
All software code, customer data, algorithms, and business plans developed during employment are exclusive property of HR Nexus. Strict non-disclosure agreements govern proprietary technology.

4. Whistleblower Protection:
Employees may report ethical violations, financial misconduct, or safety breaches anonymously via ethics@hrnexus.ai without fear of retaliation or adverse employment actions.""",
                "Specifies anti-harassment, zero tolerance discrimination, moonlighting restrictions, and whistleblower protections.",
                "2025-10-01"
            ),
            (
                "Attendance and Hybrid Work SOP", "Operations", "2.1",
                """HR NEXUS ENTERPRISES - ATTENDANCE & HYBRID WORK POLICY
1. Core Working Hours:
Standard business hours are 9:00 AM to 5:00 PM in the employee's local time zone. Core collaboration hours where all team members must be reachable on Slack are 10:00 AM to 3:00 PM EST.

2. Hybrid Schedule Guidelines:
Employees designated as 'Hybrid' are required to work from their designated regional office at least 2 days per week (typically Tuesday and Thursday). Remote days must be logged in the HR portal.

3. Equipment and Home Office Stipend:
The IT Department provisions a high-spec MacBook Pro or ThinkPad, dual monitors upon request, and a one-time home office setup stipend of $750 USD upon successful completion of onboarding.

4. Laptop Allocation and IT Approval:
Laptop allocations are approved by the IT Infrastructure Lead and department managers during Day 1 onboarding.""",
                "Defines core hours (10 AM - 3 PM EST), 2-day hybrid office policy, $750 home office stipend, and IT laptop allocation rules.",
                "2026-01-15"
            ),
            (
                "Employee Onboarding Guidelines and SLA", "Recruitment & Onboarding", "4.0",
                """HR NEXUS ENTERPRISES - ONBOARDING GUIDELINES & SLA
1. Pre-Joining Protocol:
Upon candidate offer acceptance, the HR Onboarding Agent automatically creates the employee profile and dispatches the Pre-Joining document checklist. The candidate must submit identification, tax forms, and educational proofs at least 3 days prior to Day 1.

2. Day 1 Deliverables:
- 09:30 AM: Automated Welcome Email with corporate credentials sent.
- 10:30 AM: IT hardware orientation and 2-factor authentication setup.
- 02:00 PM: HR orientation covering benefits, leave policy, and culture.
- 04:00 PM: Department introduction with designated buddy.

3. Document Verification SLA:
HR operations must verify or reject all submitted onboarding documents within 48 business hours of candidate submission. Rejections must clearly cite missing stamps, blurriness, or expired validity.""",
                "Sets mandatory onboarding schedule for Pre-Joining, Day 1, and 48-hour document verification SLA.",
                "2026-02-01"
            ),
            (
                "End-to-End Recruitment and Hiring Policy", "Recruitment", "3.0",
                """HR NEXUS ENTERPRISES - RECRUITMENT POLICY & WORKFLOW
1. Requisition Approval Process:
Every new hire requisition must be approved by both the Department Head and the Finance Controller prior to job posting. Emergency backfills require VP authorization.

2. AI Screening & Human-in-the-Loop Governance:
AI Resume Screening serves strictly as an assist tool. Match scores evaluate skills, experience, and education matches objectively. AI systems are strictly prohibited from evaluating candidates based on gender, ethnicity, age, or marital status. Final shortlisting, rejection, and offer decisions require authorized human review and sign-off.

3. Structured Interviewing:
All candidates must complete structured STAR (Situation, Task, Action, Result) behavioral and technical rounds. Interviewers must submit feedback within 24 hours of interview completion.""",
                "Mandates dual requisition approval, strict AI anti-bias safeguards, STAR structured interviewing, and 24-hr feedback SLAs.",
                "2026-01-10"
            )
        ]
        cursor.executemany("""
            INSERT INTO hr_policies (title, category, version, content, summary, effective_date)
            VALUES (?, ?, ?, ?, ?, ?);
        """, policies)

        # 17. Workflow Executions (Active workflows)
        workflows = [
            (
                "Recruitment", "Recruitment Lifecycle - Senior Python Developer", 1,
                "Candidate Final Selection & Offer Preparation", "In Progress", "Sarah Jenkins",
                json.dumps({"candidate_id": 1, "requisition_id": 1, "next_step": "Draft Offer Letter"}),
                "1. Requisition Created -> 2. AI JD Generated -> 3. Resumes Screened -> 4. Technical Round 1 Completed -> 5. Architecture Round 2 Completed."
            ),
            (
                "Onboarding", "Employee Onboarding - Aisha Khan", 1,
                "Day 1 Orientation & IT Provisioning", "In Progress", "Sarah Jenkins",
                json.dumps({"employee_id": 1, "joining_date": "2026-03-15", "progress": 65}),
                "1. Offer Accepted -> 2. Employee Profile Created -> 3. ID Generated (EMP-2026-001) -> 4. Pre-Joining Docs Uploaded."
            )
        ]
        cursor.executemany("""
            INSERT INTO workflow_executions (
                workflow_type, workflow_name, entity_id, current_step,
                status, initiated_by, payload_json, execution_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, workflows)

        # 18. Audit Logs
        logs = [
            ("JOB_REQUISITION_CREATED", "Job Requisitions", "Adil Admin", "Created requisition REQ-2026-001 for Senior Python Developer"),
            ("JOB_REQUISITION_APPROVED", "Job Requisitions", "Adil Admin", "Approved requisition REQ-2026-001"),
            ("AI_SCREENING_EXECUTED", "Resume Screening", "Sarah Jenkins", "AI parsed and scored 5 candidates for Senior Python Developer"),
            ("OFFER_LETTER_GENERATED", "Offer Management", "Sarah Jenkins", "Generated offer letter OFF-2026-001 for Aisha Khan ($68,000 USD)"),
            ("ONBOARDING_INITIALIZED", "Employee Onboarding", "Sarah Jenkins", "Initialized onboarding checklist for EMP-2026-001 Aisha Khan")
        ]
        cursor.executemany("""
            INSERT INTO audit_logs (user_action, module, performed_by, details)
            VALUES (?, ?, ?, ?);
        """, logs)

        # 19. Notifications
        notifications = [
            ("Offer Acceptance", "Aisha Khan has formally accepted the offer for HR Executive! Onboarding checklist ready.", "HR Manager", 0, "High"),
            ("Interview Completed", "David Chen submitted Round 2 feedback for Alex Rivera (Rating: 9.2/10).", "HR Manager", 0, "Normal"),
            ("Pending Document Verification", "Aisha Khan uploaded degree certificate; verification SLA is 48 hours.", "HR Manager", 0, "Normal"),
            ("New Requisition Draft", "Marcus Vance submitted requisition REQ-2026-005 Senior Product Manager for review.", "Admin", 0, "High")
        ]
        cursor.executemany("""
            INSERT INTO notifications (title, message, recipient_role, is_read, priority)
            VALUES (?, ?, ?, ?, ?);
        """, notifications)

        print("HR Nexus AI: Database seeded successfully with 5 jobs, 20 candidates, 10 interviews, 5 employees, 10 onboarding tasks, and 5 HR policies.")

    # Expand to 50 comprehensive candidate profiles
    from database.seed_50_candidates import seed_50_candidates
    seed_50_candidates()

if __name__ == "__main__":
    seed_all_data()

