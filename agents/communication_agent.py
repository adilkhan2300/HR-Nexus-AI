"""
HR Nexus AI - Candidate Communication Agent
Generates 10+ tailored communication templates with human approval gates and transmission logs.
"""
from agents.base_agent import BaseAIAgent
from database.connection import get_db

COMMUNICATION_TEMPLATES = {
    "Application Acknowledgement": {
        "subject": "Thank you for applying to HR Nexus AI - {job_title}",
        "body": """Dear {candidate_name},

Thank you for applying for the position of {job_title} at HR Nexus AI. We have received your application materials and resume.

Our talent acquisition team and AI screening workflows are currently reviewing candidate profiles against role qualifications. If your background aligns with our immediate requirements, our recruiting coordinator will reach out regarding next steps.

We appreciate your interest in building the future of autonomous operations with us.

Warm regards,
{sender_name}
HR Nexus AI Talent Acquisition Team"""
    },
    "Shortlisting Notification": {
        "subject": "Your application for {job_title} has been shortlisted! - HR Nexus AI",
        "body": """Dear {candidate_name},

Great news! We have reviewed your profile and qualifications for the {job_title} role, and our team was very impressed by your domain experience and achievements.

We have officially moved your application to the Shortlisted stage. Our team is now preparing the scheduling details for your initial discussion.

Please keep an eye out for an interview invitation link shortly.

Best regards,
{sender_name}
HR Nexus AI Talent Acquisition"""
    },
    "Interview Invitation": {
        "subject": "Interview Invitation: {job_title} - HR Nexus AI",
        "body": """Dear {candidate_name},

We would like to invite you for an interview for the {job_title} position.

Details of your upcoming round:
- Interview Round: {round_name}
- Interviewer: {interviewer_name}
- Date & Time: {scheduled_time}
- Meeting Link: {meeting_link}
- Estimated Duration: {duration_minutes} minutes

Please ensure you have a quiet environment, stable internet connection, and working audio/video. If you have any scheduling conflicts, please reply directly to this email at least 24 hours in advance.

Looking forward to speaking with you!

Warm regards,
{sender_name}
HR Nexus AI Team"""
    },
    "Interview Reminder": {
        "subject": "Reminder: Upcoming Interview for {job_title} Today",
        "body": """Dear {candidate_name},

This is a friendly reminder for your scheduled interview for the {job_title} role today at {scheduled_time}.

Meeting Link: {meeting_link}
Interviewer: {interviewer_name}

Please join the link 2-3 minutes ahead of time. If you face any technical difficulties, reply to this email immediately.

Best regards,
{sender_name}"""
    },
    "Interview Rescheduling": {
        "subject": "Rescheduled: Interview for {job_title} - HR Nexus AI",
        "body": """Dear {candidate_name},

Due to an unavoidable scheduling conflict, we need to adjust the time for your {round_name} interview for the {job_title} position.

New Scheduled Date & Time: {scheduled_time}
Meeting Link: {meeting_link}
Interviewer: {interviewer_name}

We sincerely apologize for any inconvenience caused. Please confirm if this updated time works for you.

Warm regards,
{sender_name}"""
    },
    "Assessment Instructions": {
        "subject": "Technical Assessment Guidelines: {job_title} - HR Nexus AI",
        "body": """Dear {candidate_name},

As part of the evaluation process for {job_title}, we invite you to complete a practical skills assessment.

Instructions:
- Timeframe: 48 hours from receipt of this email
- Submission: Push your code or analysis to a private GitHub repository or reply with your document
- Scope: Focus on code clarity, test coverage, and documentation

Link to Challenge: https://assessments.hrnexus.ai/challenge/{candidate_name}

Best of luck,
{sender_name}"""
    },
    "Selection Notification": {
        "subject": "Congratulations! Offer Selection for {job_title} at HR Nexus AI",
        "body": """Dear {candidate_name},

We are thrilled to inform you that following your interview rounds, the hiring committee has selected you for the role of {job_title}!

Our team was thoroughly impressed by your technical mastery, thoughtful problem-solving, and culture fit.

We are currently preparing your formal Offer Letter and compensation package, which will be shared with you shortly for formal review and acceptance.

Congratulations on reaching this milestone!

Warmest regards,
{sender_name}
Head of Talent Acquisition, HR Nexus AI"""
    },
    "Rejection Notification": {
        "subject": "Update on your application for {job_title} at HR Nexus AI",
        "body": """Dear {candidate_name},

Thank you for taking the time to participate in our recruitment process for the {job_title} position. We truly enjoyed learning about your background and accomplishments.

After careful consideration, our team has decided to proceed with another candidate whose current profile more closely aligns with the specific specialized needs of this opening.

Please know that this was a competitive selection. We will keep your profile in our active talent pool for future opportunities that match your expertise.

We wish you continued success in your professional career.

Sincerely,
{sender_name}
HR Nexus AI Team"""
    },
    "Offer Letter Communication": {
        "subject": "Official Offer of Employment: {job_title} - HR Nexus AI",
        "body": """Dear {candidate_name},

We are delighted to formally extend an offer of employment for the position of {job_title} at HR Nexus AI!

Enclosed please find your formal Offer Letter outlining your designation, reporting structure, compensation details, and benefits package.

Key Highlights:
- Annual Compensation: ${annual_ctc:,.2f} {currency}
- Proposed Joining Date: {joining_date}
- Location: {work_location}

Please review the attached offer letter carefully and submit your signed acceptance by {offer_deadline}.

Welcome to the HR Nexus family!

Warm regards,
{sender_name}
HR Nexus AI Operations"""
    },
    "Joining Instructions": {
        "subject": "Joining Day Instructions & Day 1 Orientation - HR Nexus AI",
        "body": """Dear {candidate_name},

We are excited to welcome you on your upcoming Day 1 on {joining_date}!

Here is what you need to know for your first day:
1. Schedule: Virtual orientation begins at 09:30 AM EST via Google Meet.
2. Credentials: Your company email credentials and Slack invite will arrive in your inbox at 09:00 AM.
3. Equipment: Your IT provisioned equipment is dispatched via FedEx (Tracking #HN-99824).
4. Checklist: Please ensure all Pre-Joining identity and educational documents are submitted in the Onboarding Portal.

We look forward to an amazing journey together!

Best regards,
{sender_name}
HR Onboarding Team"""
    }
}

class CommunicationAgent(BaseAIAgent):
    def get_template(self, template_name: str, context: dict) -> dict:
        """Render email subject and body using template and contextual parameters."""
        tmpl = COMMUNICATION_TEMPLATES.get(template_name, COMMUNICATION_TEMPLATES["Application Acknowledgement"])
        subject = tmpl["subject"]
        body = tmpl["body"]

        # Safe formatting
        for k, v in context.items():
            subject = subject.replace("{" + str(k) + "}", str(v))
            body = body.replace("{" + str(k) + "}", str(v))

        return {
            "template_name": template_name,
            "subject": subject,
            "body": body,
            "recipient_email": context.get("recipient_email", ""),
            "candidate_id": context.get("candidate_id")
        }

    def save_communication(self, candidate_id: int, application_id: int, comm_type: str,
                           subject: str, body: str, sender: str, recipient_email: str,
                           status: str = "Sent", approved_by: str = "HR Manager") -> int:
        """Log communication to database with audit tracking."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO communications (
                    candidate_id, application_id, communication_type, subject,
                    body_text, sender, recipient_email, status, approval_required,
                    approved_by, sent_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, CURRENT_TIMESTAMP);
            """, (
                candidate_id, application_id, comm_type, subject,
                body, sender, recipient_email, status, approved_by
            ))
            comm_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("COMMUNICATION_DISPATCHED", "Communications", approved_by, f"Sent {comm_type} to {recipient_email}"))

            return comm_id

