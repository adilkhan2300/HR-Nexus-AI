"""
HR Nexus AI - SQLite Database Schema and Connection Manager
Implements all 19 relational tables specified in prompt.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import DATABASE_PATH

def get_connection():
    """Return a sqlite3 connection with dict-like row access."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    """Context manager for safe transactional database queries."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Create all 19 database tables with proper constraints."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Admin', 'HR Manager', 'Interviewer / Dept Manager')),
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Job Requisitions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_requisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            vacancies INTEGER DEFAULT 1,
            experience_required TEXT NOT NULL,
            min_salary REAL,
            max_salary REAL,
            salary_currency TEXT DEFAULT 'USD',
            hiring_manager TEXT NOT NULL,
            priority TEXT DEFAULT 'Medium',
            qualifications TEXT,
            technical_skills TEXT,
            soft_skills TEXT,
            job_description TEXT,
            approval_status TEXT DEFAULT 'Pending' CHECK(approval_status IN ('Draft', 'Pending', 'Approved', 'Rejected', 'Closed')),
            approved_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Job Descriptions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requisition_id INTEGER,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            overview TEXT,
            responsibilities TEXT,
            qualifications TEXT,
            technical_skills TEXT,
            soft_skills TEXT,
            experience_requirements TEXT,
            salary_range TEXT,
            company_expectations TEXT,
            interview_questions TEXT,
            hiring_channels TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (requisition_id) REFERENCES job_requisitions(id) ON DELETE SET NULL
        );
        """)

        # 4. Candidates
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            location TEXT,
            highest_education TEXT,
            total_experience_years REAL DEFAULT 0,
            current_organization TEXT,
            current_designation TEXT,
            notice_period_days INTEGER DEFAULT 30,
            expected_salary REAL,
            consent_given INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Resumes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            raw_text TEXT,
            parsed_json TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );
        """)

        # 6. Candidate Skills
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_type TEXT CHECK(skill_type IN ('Technical', 'Soft', 'Domain', 'Tool')),
            proficiency_level TEXT DEFAULT 'Intermediate',
            verified INTEGER DEFAULT 0,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
        );
        """)

        # 7. Applications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_code TEXT UNIQUE NOT NULL,
            candidate_id INTEGER NOT NULL,
            requisition_id INTEGER NOT NULL,
            stage TEXT DEFAULT 'Applied',
            source TEXT DEFAULT 'Portal',
            applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status_notes TEXT,
            hr_manager_assigned TEXT,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (requisition_id) REFERENCES job_requisitions(id) ON DELETE CASCADE
        );
        """)

        # 8. Screening Results
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS screening_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER UNIQUE NOT NULL,
            candidate_id INTEGER NOT NULL,
            requisition_id INTEGER NOT NULL,
            skills_match_score REAL DEFAULT 0,
            experience_match_score REAL DEFAULT 0,
            education_match_score REAL DEFAULT 0,
            overall_match_score REAL DEFAULT 0,
            matching_skills TEXT,
            missing_skills TEXT,
            candidate_summary TEXT,
            verification_flags TEXT,
            recommendation TEXT,
            screening_rationale TEXT,
            screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            human_reviewed INTEGER DEFAULT 0,
            reviewed_by TEXT,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (requisition_id) REFERENCES job_requisitions(id) ON DELETE CASCADE
        );
        """)

        # 9. Interviews
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_code TEXT UNIQUE NOT NULL,
            application_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            requisition_id INTEGER NOT NULL,
            round_name TEXT NOT NULL,
            round_number INTEGER DEFAULT 1,
            interviewer_name TEXT NOT NULL,
            interviewer_email TEXT,
            scheduled_time TIMESTAMP NOT NULL,
            duration_minutes INTEGER DEFAULT 45,
            meeting_link TEXT,
            status TEXT DEFAULT 'Scheduled' CHECK(status IN ('Scheduled', 'Completed', 'Rescheduled', 'Cancelled', 'No Show')),
            attendance_confirmed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (requisition_id) REFERENCES job_requisitions(id) ON DELETE CASCADE
        );
        """)

        # 10. Interview Feedback
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            interviewer_name TEXT NOT NULL,
            technical_score REAL DEFAULT 0,
            communication_score REAL DEFAULT 0,
            problem_solving_score REAL DEFAULT 0,
            competency_score REAL DEFAULT 0,
            experience_score REAL DEFAULT 0,
            overall_rating REAL DEFAULT 0,
            strengths TEXT,
            weaknesses TEXT,
            detailed_comments TEXT,
            recommendation TEXT CHECK(recommendation IN ('Strong Hire', 'Hire', 'Hold', 'Reject')),
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
        );
        """)

        # 11. Communications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            application_id INTEGER,
            communication_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            body_text TEXT NOT NULL,
            sender TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            status TEXT DEFAULT 'Draft' CHECK(status IN ('Draft', 'Sent', 'Scheduled', 'Failed')),
            approval_required INTEGER DEFAULT 1,
            approved_by TEXT,
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE SET NULL
        );
        """)

        # 12. Offers
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_code TEXT UNIQUE NOT NULL,
            application_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            requisition_id INTEGER NOT NULL,
            designation TEXT NOT NULL,
            department TEXT NOT NULL,
            reporting_manager TEXT NOT NULL,
            joining_date DATE NOT NULL,
            annual_ctc REAL NOT NULL,
            currency TEXT DEFAULT 'USD',
            work_location TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            terms_and_conditions TEXT,
            offer_status TEXT DEFAULT 'Draft' CHECK(offer_status IN ('Draft', 'Approved by HR', 'Released', 'Accepted', 'Declined', 'Expired')),
            pdf_path TEXT,
            docx_path TEXT,
            hr_approved_by TEXT,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
            FOREIGN KEY (requisition_id) REFERENCES job_requisitions(id) ON DELETE CASCADE
        );
        """)

        # 13. Employees
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            personal_phone TEXT,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            reporting_manager TEXT NOT NULL,
            joining_date DATE NOT NULL,
            work_location TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            employment_status TEXT DEFAULT 'Probation' CHECK(employment_status IN ('Probation', 'Active', 'Confirmed', 'Resigned', 'Terminated')),
            onboarding_progress INTEGER DEFAULT 0,
            doc_verification_status TEXT DEFAULT 'Pending' CHECK(doc_verification_status IN ('Pending', 'Partial', 'Verified', 'Rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 14. Employee Documents
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            document_type TEXT NOT NULL,
            document_name TEXT NOT NULL,
            file_path TEXT,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Submitted', 'Under Verification', 'Verified', 'Rejected')),
            verification_notes TEXT,
            verified_by TEXT,
            verified_at TIMESTAMP,
            uploaded_at TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        """)

        # 15. Onboarding Tasks
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            phase TEXT NOT NULL CHECK(phase IN ('Pre-Joining', 'Day 1', 'First Week', 'First 30 Days')),
            task_title TEXT NOT NULL,
            task_description TEXT,
            assigned_to TEXT NOT NULL,
            due_date DATE,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Completed', 'Overdue')),
            completed_at TIMESTAMP,
            completed_by TEXT,
            notes TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        );
        """)

        # 16. HR Policies
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hr_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            version TEXT DEFAULT '1.0',
            content TEXT NOT NULL,
            summary TEXT,
            effective_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 17. Workflow Executions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_type TEXT NOT NULL, -- 'Recruitment' or 'Onboarding'
            workflow_name TEXT NOT NULL,
            entity_id INTEGER, -- application_id or employee_id
            current_step TEXT NOT NULL,
            status TEXT DEFAULT 'In Progress' CHECK(status IN ('In Progress', 'Awaiting Approval', 'Completed', 'Failed')),
            initiated_by TEXT NOT NULL,
            payload_json TEXT,
            execution_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 18. Audit Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_action TEXT NOT NULL,
            module TEXT NOT NULL,
            performed_by TEXT NOT NULL,
            details TEXT,
            ip_address TEXT DEFAULT '127.0.0.1',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 19. Notifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            recipient_role TEXT,
            is_read INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'Normal' CHECK(priority IN ('Low', 'Normal', 'High', 'Urgent')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        print("HR Nexus AI: Database schema initialized successfully.")

