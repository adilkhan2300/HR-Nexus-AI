"""
HR Nexus AI - Multi-Channel Notification Service (WhatsApp, SMS & Email)
Provides unified candidate and recruiter notification orchestration across:
1. WhatsApp (CallMeBot free push, Twilio, Meta Cloud API, 1-Click wa.me)
2. SMS (Fast2SMS API, Twilio SMS, 1-Click native sms: URI)
3. Email (SMTP/Gmail TLS transmission, 1-Click native mailto: URI, DB logging)
"""
import os
import smtplib
import urllib.parse
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database.connection import get_db
from services.whatsapp_service import WhatsAppNotificationService

class MultiChannelNotificationService:
    def __init__(self):
        self.wa_service = WhatsAppNotificationService()
        self.recipient_phone = os.getenv("NOTIFICATION_PHONE", os.getenv("WHATSAPP_RECIPIENT_PHONE", "+917888270396"))
        self.recipient_email = os.getenv("NOTIFICATION_EMAIL", "recruiter@hrnexus.ai")
        self.hr_email = os.getenv("HR_EMAIL", "hr@hrnexus.ai")

        # SMTP Email Config
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user or "notifications@hrnexus.ai")

        # SMS Config
        self.fast2sms_key = os.getenv("FAST2SMS_API_KEY", "")
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_sms_from = os.getenv("TWILIO_SMS_NUMBER", "")

    def clean_phone(self, phone: str) -> str:
        """Sanitize phone number to standard 10 or 12 digits."""
        digits = "".join(filter(str.isdigit, phone or ""))
        if len(digits) == 10:
            digits = "91" + digits
        return digits

    # ==========================================
    # 1. EMAIL CHANNEL DISPATCH
    # ==========================================
    def format_interview_email(self, candidate_name: str, candidate_code: str,
                               job_title: str, department: str,
                               round_name: str, round_number: int,
                               interviewer_name: str, interviewer_email: str,
                               scheduled_time: str, duration_minutes: int,
                               meeting_link: str) -> tuple[str, str]:
        """Generate subject and formatted email body for interview meeting."""
        subject = f"Interview Scheduled: {candidate_name} - {round_name} ({job_title})"
        body = f"""Dear Hiring Team & {interviewer_name},

A new interview round has been booked on the HR Nexus AI calendar.

MEETING BRIEFING & DETAILS:
============================================================
• Candidate: {candidate_name} (#{candidate_code})
• Position: {job_title} ({department})
• Interview Round: {round_name} (Round #{round_number})
• Date & Scheduled Time: {scheduled_time}
• Estimated Duration: {duration_minutes} Minutes
• Assigned Interviewer: {interviewer_name} ({interviewer_email})

JOIN MEETING LINK:
{meeting_link}

STRUCTURED INTERVIEW AGENDA:
1. Candidate Intro & Portfolio Review (5 mins)
2. Core Technical Competency & Architectural Depth (20 mins)
3. Practical Scenario / Live Task Review (15 mins)
4. STAR Behavioral & Culture Alignment (5 mins)

EVALUATION INSTRUCTIONS:
Please join the Google Meet link 2-3 minutes ahead of schedule. Post-interview, submit your evaluation scores (Technical Mastery, Communication, Problem Solving, Competency, Experience) via the HR Nexus AI portal.

Warm regards,
HR Nexus AI Autonomous Recruitment Agent
operations@hrnexus.ai
"""
        return subject, body

    def format_shortlist_email(self, candidate_name: str, candidate_code: str,
                               job_title: str, department: str,
                               match_score: float, experience_years: float,
                               current_org: str, key_skills: str,
                               missing_skills: str) -> tuple[str, str]:
        """Generate subject and formatted email body for candidate shortlisting."""
        subject = f"Candidate Shortlisted: {candidate_name} ({match_score}% Match) - {job_title}"
        body = f"""Dear Talent Acquisition Team,

Candidate {candidate_name} has officially met all evaluation thresholds and has been moved to the SHORTLISTED stage!

CANDIDATE DOSSIER:
============================================================
• Full Name: {candidate_name} (#{candidate_code})
• Job Opening: {job_title} ({department})
• AI Match Score: {match_score}%
• Total Experience: {experience_years} Years ({current_org})
• Matching Qualifications: {key_skills}
• Identified Skill Gaps: {missing_skills or 'None noted'}

NEXT RECOMMENDED STEPS:
1. Schedule Round 1 Technical Interview.
2. Confirm interviewer panel availability.
3. Transmit meeting invitation and candidate briefing.

Regards,
HR Nexus AI Talent Acquisition Engine
"""
        return subject, body

    def get_mailto_link(self, to_email: str, subject: str, body: str) -> str:
        """Generate a 1-click mailto: deep link for instant default client composition."""
        enc_sub = urllib.parse.quote(subject)
        enc_body = urllib.parse.quote(body)
        return f"mailto:{to_email}?subject={enc_sub}&body={enc_body}"

    def send_email(self, to_email: str, subject: str, body: str) -> dict:
        """Dispatch email via SMTP (if configured) or prepare 1-click mailto: link."""
        status = "Ready for 1-Click Email Client Dispatch"
        mailto_link = self.get_mailto_link(to_email, subject, body)

        if self.smtp_user and self.smtp_pass:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.smtp_from
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_from, [to_email], msg.as_string())
                server.quit()
                status = f"Dispatched via SMTP Server ({self.smtp_host})"
            except Exception as e:
                status = f"SMTP Attempt Failed ({str(e)[:40]}). 1-Click Mailto Ready."

        # Log in communications database
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO communications (candidate_id, communication_type, subject, body, sender, recipient_email, status, approved_by)
                    VALUES (1, 'Notification Email', ?, ?, 'HR Nexus Agent', ?, ?, 'System');
                """, (subject, body, to_email, status))
        except Exception:
            pass

        return {
            "status": status,
            "recipient_email": to_email,
            "subject": subject,
            "body": body,
            "mailto_link": mailto_link
        }

    # ==========================================
    # 2. SMS CHANNEL DISPATCH
    # ==========================================
    def format_interview_sms(self, candidate_name: str, job_title: str,
                             round_name: str, scheduled_time: str,
                             meeting_link: str) -> str:
        """Concise, high-impact SMS message with meeting link and schedule."""
        return (
            f"HR NEXUS ALERT: Interview booked for {candidate_name} ({job_title})! "
            f"Round: {round_name}. "
            f"Time: {scheduled_time}. "
            f"Join Meet: {meeting_link} - HR Nexus AI"
        )

    def format_shortlist_sms(self, candidate_name: str, job_title: str, match_score: float) -> str:
        """Concise SMS shortlist notification."""
        return (
            f"HR NEXUS ALERT: {candidate_name} has been SHORTLISTED for {job_title} "
            f"with an AI match score of {match_score}%! Please review & schedule interview in HR Portal."
        )

    def get_sms_link(self, phone: str, message: str) -> str:
        """Generate native 1-click sms: URI for mobile and desktop SMS apps."""
        clean = self.clean_phone(phone)
        enc_msg = urllib.parse.quote(message)
        return f"sms:+{clean}?body={enc_msg}"

    def send_sms(self, to_phone: str, message: str) -> dict:
        """Dispatch SMS via Fast2SMS / Twilio or prepare 1-click native SMS URI."""
        clean = self.clean_phone(to_phone)
        status = "Ready for 1-Click SMS App Dispatch"
        sms_link = self.get_sms_link(to_phone, message)

        # 1. Try Fast2SMS (popular Indian SMS gateway)
        if self.fast2sms_key:
            try:
                # Fast2SMS requires 10-digit number for Indian delivery
                num_10 = clean[-10:]
                url = "https://www.fast2sms.com/dev/bulkV2"
                payload = {
                    "authorization": self.fast2sms_key,
                    "message": message,
                    "language": "english",
                    "route": "q",
                    "numbers": num_10
                }
                headers = {"cache-control": "no-cache"}
                res = requests.post(url, data=payload, headers=headers, timeout=8)
                if res.status_code == 200 and res.json().get("return"):
                    status = "Sent via Fast2SMS Gateway"
            except Exception as e:
                print(f"Fast2SMS error: {e}")

        # 2. Try Twilio SMS
        if status.startswith("Ready") and self.twilio_sid and self.twilio_token and self.twilio_sms_from:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
                data = {
                    "From": self.twilio_sms_from,
                    "To": f"+{clean}",
                    "Body": message
                }
                res = requests.post(url, data=data, auth=(self.twilio_sid, self.twilio_token), timeout=8)
                if res.status_code in [200, 201]:
                    status = "Sent via Twilio SMS API"
            except Exception as e:
                print(f"Twilio SMS error: {e}")

        # Log in notifications database
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (title, message, recipient_role, priority)
                    VALUES (?, ?, 'HR Manager', 'High');
                """, (f"SMS Dispatched to {to_phone}", message[:120]))
        except Exception:
            pass

        return {
            "status": status,
            "recipient_phone": to_phone,
            "message": message,
            "sms_link": sms_link
        }

    # ==========================================
    # 3. UNIFIED MULTI-CHANNEL DISPATCH
    # ==========================================
    def send_interview_multi_channel(self, candidate_name: str, candidate_code: str,
                                    job_title: str, department: str,
                                    round_name: str, round_number: int,
                                    interviewer_name: str, interviewer_email: str,
                                    scheduled_time: str, duration_minutes: int,
                                    meeting_link: str, phone: str = None,
                                    email: str = None, candidate_phone: str = "",
                                    candidate_email: str = "") -> dict:
        """Simultaneously trigger WhatsApp, SMS, and Email notifications with agendas & links."""
        target_phone = phone or self.recipient_phone
        target_email = email or self.recipient_email

        # 1. WhatsApp Dispatch
        wa_result = self.wa_service.send_interview_alert(
            candidate_name=candidate_name,
            candidate_code=candidate_code,
            job_title=job_title,
            department=department,
            round_name=round_name,
            round_number=round_number,
            interviewer_name=interviewer_name,
            interviewer_email=interviewer_email,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            meeting_link=meeting_link,
            phone=target_phone,
            candidate_phone=candidate_phone,
            candidate_email=candidate_email
        )

        # 2. SMS Dispatch
        sms_body = self.format_interview_sms(
            candidate_name=candidate_name,
            job_title=job_title,
            round_name=round_name,
            scheduled_time=scheduled_time,
            meeting_link=meeting_link
        )
        sms_result = self.send_sms(target_phone, sms_body)

        # 3. Email Dispatch
        email_subj, email_body = self.format_interview_email(
            candidate_name=candidate_name,
            candidate_code=candidate_code,
            job_title=job_title,
            department=department,
            round_name=round_name,
            round_number=round_number,
            interviewer_name=interviewer_name,
            interviewer_email=interviewer_email,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            meeting_link=meeting_link
        )
        email_result = self.send_email(target_email, email_subj, email_body)

        return {
            "candidate_name": candidate_name,
            "meeting_link": meeting_link,
            "scheduled_time": scheduled_time,
            "whatsapp": wa_result,
            "sms": sms_result,
            "email": email_result
        }

    def send_shortlist_multi_channel(self, candidate_name: str, candidate_code: str,
                                    job_title: str, department: str,
                                    match_score: float, skills_score: float = 0.0,
                                    exp_score: float = 0.0, edu_score: float = 0.0,
                                    experience_years: float = 0.0, current_org: str = "",
                                    key_skills: str = "", missing_skills: str = "",
                                    phone: str = None, email: str = None) -> dict:
        """Simultaneously trigger WhatsApp, SMS, and Email shortlist notifications."""
        target_phone = phone or self.recipient_phone
        target_email = email or self.recipient_email

        # 1. WhatsApp Dispatch
        wa_result = self.wa_service.send_shortlist_alert(
            candidate_name=candidate_name,
            job_title=job_title,
            candidate_code=candidate_code,
            department=department,
            match_score=match_score,
            skills_score=skills_score,
            exp_score=exp_score,
            edu_score=edu_score,
            experience_years=experience_years,
            current_org=current_org,
            key_skills=key_skills,
            missing_skills=missing_skills,
            phone=target_phone
        )

        # 2. SMS Dispatch
        sms_body = self.format_shortlist_sms(candidate_name, job_title, match_score)
        sms_result = self.send_sms(target_phone, sms_body)

        # 3. Email Dispatch
        email_subj, email_body = self.format_shortlist_email(
            candidate_name=candidate_name,
            candidate_code=candidate_code,
            job_title=job_title,
            department=department,
            match_score=match_score,
            experience_years=experience_years,
            current_org=current_org,
            key_skills=key_skills,
            missing_skills=missing_skills
        )
        email_result = self.send_email(target_email, email_subj, email_body)

        return {
            "candidate_name": candidate_name,
            "whatsapp": wa_result,
            "sms": sms_result,
            "email": email_result
        }

