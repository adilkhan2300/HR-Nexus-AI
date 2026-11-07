# HR Nexus AI – Intelligent Recruitment & Employee Onboarding Agent

> **Subject:** AI Agents & Autonomous Business Operations  
> **Course Assignment:** Comprehensive Final Project  
> **Architecture:** Autonomous Multi-Agent System with Human-in-the-Loop Governance

---

## 🌟 Executive Summary

**HR Nexus AI** is an enterprise-grade autonomous AI HR department system designed to manage the end-to-end employee lifecycle—from initial manpower planning and job requisitioning to recruitment, resume screening, multi-round structured interviewing, offer issuance, and 4-phase employee onboarding.

Unlike static dashboards or simple chatbots, **HR Nexus AI** coordinates intelligent AI agents that analyze instructions, extract candidate attributes, calculate explainable match scores, generate legal documents, and orchestrate business operations while strictly enforcing **human-in-the-loop** verification checkpoints and responsible AI non-discrimination standards.

---

## 🏗️ System Architecture & Technology Stack

- **Frontend:** Streamlit with custom CSS responsive enterprise SaaS layout, glowing KPI cards, and Kanban pipeline tracking.
- **Backend:** Python 3.13 modular agentic architecture.
- **Database:** SQLite relational engine implementing **19 relational tables** with foreign key constraints and transactional integrity.
- **AI Engine:** Dual-mode architecture supporting **OpenAI API (GPT-4o-mini)**, **Google Gemini API (1.5 Flash)**, and an intelligent **Offline Heuristic Agent Engine** for 100% functional demo mode without external API keys.
- **Document Processing & Generation:** 
  - `PyPDF2` for PDF resume extraction and policy document ingestion.
  - `python-docx` for parsing DOCX resumes and generating Word offer letters and job descriptions.
  - `ReportLab` for generating professional, printable PDF offer letters and Non-Disclosure Agreements (NDAs).
- **Data Analytics & Visualization:** `Pandas`, `NumPy`, and `Plotly` for dynamic funnels, channel source distributions, and SLA progress tracking.

---

## 🏛️ Database Design (19 Relational Tables)

1. `users` – System users with role definitions (`Admin`, `HR Manager`, `Interviewer / Dept Manager`).
2. `job_requisitions` – Manpower requisitions with priority, salary brackets, and approval states.
3. `job_descriptions` – AI-generated and HR-customized role specifications and question banks.
4. `candidates` – Applicant master repository with education, experience, notice periods, and salary expectations.
5. `resumes` – Raw text, file paths, and parsed JSON payload for candidate resumes.
6. `candidate_skills` – Normalized technical and soft skills with verification tags.
7. `applications` – Candidate applications mapped to requisitions across **12 pipeline stages**.
8. `screening_results` – Explainable AI scoring (Skills %, Experience %, Education %, Overall %), missing skills, and audit flags.
9. `interviews` – Multi-round interview schedule, assigned panelists, duration, and Google Meet integration.
10. `interview_feedback` – 5-parameter structured evaluations (Technical, Communication, Problem Solving, Competencies, Experience).
11. `communications` – Automated email drafts across 10 lifecycle milestones with approval tracking.
12. `offers` – Compensation proposals, designations, reporting lines, and HR sign-off states.
13. `employees` – Central master employee database with probation and onboarding progress tracking.
14. `employee_documents` – Statutory documents with 48-hour SLA verification tracking (`Pending`, `Submitted`, `Under Verification`, `Verified`, `Rejected`).
15. `onboarding_tasks` – 4-phase onboarding tasks (`Pre-Joining`, `Day 1`, `First Week`, `First 30 Days`).
16. `hr_policies` – Corporate handbooks and SOPs indexed for RAG question answering.
17. `workflow_executions` – State machine tracking multi-step autonomous recruitment and onboarding operations.
18. `audit_logs` – Immutable audit trail recording user actions, timestamps, and modules.
19. `notifications` – System alerts and reminders for pending approvals and milestones.

---

## 🚀 Key Functional Modules (15 Navigation Views)

| # | Module | Core Functionality |
|---|---|---|
| **1** | **Executive Dashboard** | Real-time KPIs, recruitment funnel, department-wise headcount, active workflows, and pending HR approval alerts. |
| **2** | **AI HR Agent** | Natural language conversational command center converting English instructions into actionable workflows. |
| **3** | **Job Requisitions** | Manpower requisition creation, approval workflows, and AI talent requirement analyzers. |
| **4** | **JD Generator** | Structured JD generator producing role overviews, bulleted responsibilities, qualifications, and STAR questions. |
| **5** | **Candidate Management** | 12-stage candidate pipeline, single and bulk resume ingestion (PDF/DOCX), and search directory. |
| **6** | **Resume Screening** | Explainable AI qualification matching, gap analysis, and strict anti-bias safeguards. |
| **7** | **Candidate Shortlisting** | Multi-candidate ranking, side-by-side comparative matrix, and HR shortlist approval gates. |
| **8** | **Interview Management** | Multi-round interview booking, STAR question bank generation, and structured 5-metric scoring forms. |
| **9** | **Communication Center** | 10 personalized email templates (invitations, reminders, offers, rejections) with human sign-off before dispatch. |
| **10** | **Offer Document Hub** | Automated generation of downloadable PDF & DOCX offer letters and NDAs. |
| **11** | **Employee Onboarding** | 4-phase onboarding management (Pre-Joining, Day 1, Week 1, Month 1) and document verification SLA tracker. |
| **12** | **Employee Database** | Central employee repository with role-based confidentiality and status editing. |
| **13** | **HR Policies & SOPs** | RAG-based knowledge assistant providing answers with exact document and section citations. |
| **14** | **Analytics & Reports** | Dynamic Plotly charts for candidate source distribution, stage funnels, and department onboarding progress. |
| **15** | **Settings & Audit Logs** | Role switcher, API key management, demo mode toggle, immutable audit logs, and data reset. |

---

## ⚖️ Responsible AI & Ethical Safeguards

1. **Strict Non-Discrimination:** Candidate scoring is strictly confined to verifiable job qualifications, technical skills, and experience duration. Gender, age, ethnicity, religion, marital status, and photos are explicitly prohibited from influencing scores.
2. **Human-in-the-Loop Governance:** AI agents **never** autonomously reject candidates, issue legal employment contracts, or alter employment status without human authorization.
3. **Transparent Explainability:** Every screening score produces an explainable rationale detailing exactly which skills matched, which were missing, and any verification flags requiring human review.

---

## 🛠️ Installation & Setup Guide

### 1. Prerequisites
- Python 3.10 to 3.13 installed.
- Git (optional).

### 2. Clone or Extract Project
Navigate to the project root directory:
```bash
cd "c:\Users\adil2\OneDrive\Desktop\Assignments\Shayam Sir IA\Final Project 2"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Add your `OPENAI_API_KEY` or `GEMINI_API_KEY` if you wish to use live cloud LLMs.  
*(Note: If left empty, HR Nexus AI runs seamlessly in **Demo Mode** with realistic offline heuristics!)*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Testing & Verification Guide

1. **Dashboard:** View live metrics loaded from sample database (50 candidates across 12 pipeline stages).
2. **AI HR Agent:** Click quick action chips (e.g. *"Screen all uploaded resumes for Senior Python Developer"*) or type natural language instructions.
3. **Resume Screening:** Open View 6, select *"Senior Python Developer"*, and click *"Start Autonomous AI Screening"*. Observe the explainable scores and verification flags.
4. **Offer Management:** Open View 10, select an eligible candidate, draft an offer, and download the generated PDF or Word (.docx) document.
5. **Onboarding:** Open View 11, review the 4-phase checklist for *Aisha Khan*, verify her documents, and check progress updates.
6. **Policy RAG:** Open View 13 and ask *"What is the company leave policy?"* or *"Who approves laptop allocation?"* to verify exact citations.

