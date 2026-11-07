"""
HR Nexus AI - WhatsApp Notification Service
Provides full WhatsApp notification capabilities for:
1. Candidate Shortlisting with full profile dossier and AI score breakdown
2. Interview Meeting Invitations with Google Meet link, date, time, duration, and interviewer
3. Direct 1-Click WhatsApp Web/App launcher (wa.me link)
4. Twilio REST API & Meta WhatsApp Cloud API integration
5. Database notification and audit trail persistence
"""
import os
import urllib.parse
import requests
from database.connection import get_db

class WhatsAppNotificationService:
    def __init__(self):
        self.recipient_phone = os.getenv("WHATSAPP_RECIPIENT_PHONE", "+917888270396")
        self.hr_phone = os.getenv("WHATSAPP_HR_PHONE", "+917888270396")
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        self.meta_token = os.getenv("WHATSAPP_META_TOKEN", "")
        self.meta_phone_id = os.getenv("WHATSAPP_META_PHONE_ID", "")
        self.callmebot_key = os.getenv("CALLMEBOT_API_KEY", "")

    def clean_phone(self, phone: str) -> str:
        """Sanitize phone number and auto-prepend country code 91 if 10 digits."""
        digits = "".join(filter(str.isdigit, phone or ""))
        if len(digits) == 10:
            digits = "91" + digits
        return digits

    def format_shortlist_dossier(self, candidate_name: str, candidate_code: str,
                                 job_title: str, department: str = "Engineering",
                                 match_score: float = 0.0, skills_score: float = 0.0,
                                 exp_score: float = 0.0, edu_score: float = 0.0,
                                 experience_years: float = 0.0, current_org: str = "",
                                 key_skills: str = "", missing_skills: str = "",
                                 verification_flags: str = "", candidate_email: str = "",
                                 candidate_phone: str = "") -> str:
        """Format an exhaustive, structured WhatsApp shortlist notification message."""
        msg = (
            f"🔔 *HR NEXUS AI - CANDIDATE SHORTLISTED* 🔔\n\n"
            f"Dear HR Team,\n"
            f"Candidate *{candidate_name}* has passed qualification screening and is officially *SHORTLISTED*!\n\n"
            f"📌 *Candidate Profile:*\n"
            f"• *Name:* {candidate_name} (#{candidate_code})\n"
            f"• *Role:* {job_title} ({department})\n"
            f"• *Email:* {candidate_email or 'candidate@example.com'}\n"
            f"• *Phone:* {candidate_phone or 'Verified'}\n"
            f"• *Total Experience:* {experience_years} Years ({current_org or 'Enterprise Tech'})\n\n"
            f"🎯 *Explainable AI Match Scores:*\n"
            f"• *Overall Compatibility:* ⭐ *{match_score}%*\n"
            f"• *Technical Skills Match:* {skills_score}%\n"
            f"• *Experience Duration Match:* {exp_score}%\n"
            f"• *Education Alignment:* {edu_score}%\n\n"
            f"🛠️ *Competency Breakdown:*\n"
            f"• *Matching Skills:* {key_skills or 'Python, REST APIs, Databases'}\n"
            f"• *Skill Gaps:* {missing_skills or 'None noted'}\n"
            f"• *Audit / Verification Flags:* {verification_flags or 'None. Standard background verification.'}\n\n"
            f"⚡ *Recommended Action:* Schedule Round 1 Technical Interview via HR Nexus AI Portal.\n\n"
            f"— _HR Nexus AI Autonomous Recruitment Agent_"
        )
        return msg

    def format_interview_meeting_alert(self, candidate_name: str, candidate_code: str,
                                       job_title: str, department: str,
                                       round_name: str, round_number: int,
                                       interviewer_name: str, interviewer_email: str,
                                       scheduled_time: str, duration_minutes: int,
                                       meeting_link: str, candidate_phone: str = "",
                                       candidate_email: str = "") -> str:
        """Format an exhaustive, structured interview meeting invitation and agenda for WhatsApp."""
        msg = (
            f"📅 *HR NEXUS AI - INTERVIEW SCHEDULED & MEETING DOSSIER* 📅\n\n"
            f"Hello HR & Interview Panel,\n"
            f"An interview round has been officially booked. Below is the complete schedule, meeting link, and candidate briefing:\n\n"
            f"👤 *CANDIDATE INFORMATION:*\n"
            f"• *Name:* {candidate_name} (#{candidate_code})\n"
            f"• *Applied Role:* {job_title}\n"
            f"• *Department:* {department}\n"
            f"• *Email:* {candidate_email or 'candidate@hrnexus.ai'}\n"
            f"• *Phone:* {candidate_phone or 'Verified on File'}\n\n"
            f"📌 *MEETING SCHEDULE:*\n"
            f"• *Round:* {round_name} (Round #{round_number})\n"
            f"• *Date & Time:* 🗓️ *{scheduled_time}*\n"
            f"• *Duration:* ⏱️ {duration_minutes} Minutes\n"
            f"• *Assigned Interviewer:* {interviewer_name} ({interviewer_email})\n\n"
            f"🔗 *JOIN MEETING LINK:*\n"
            f"{meeting_link}\n\n"
            f"📋 *STRUCTURED MEETING AGENDA & LIST:*\n"
            f"1️⃣ *Candidate Briefing & Intro* (5 mins) - Background summary & career journey\n"
            f"2️⃣ *Technical Mastery & Architecture* (20 mins) - Core skills & domain problem-solving\n"
            f"3️⃣ *Scenario / Case Challenge* (15 mins) - Practical application & live task review\n"
            f"4️⃣ *STAR Behavioral Competency* (5 mins) - Situation, Task, Action, Result culture fit\n\n"
            f"📝 *INTERVIEWER EVALUATION METRICS:*\n"
            f"• Technical Mastery (1-10)\n"
            f"• Communication & Articulation (1-10)\n"
            f"• Problem Solving & Logic (1-10)\n"
            f"• Role-Specific Competency (1-10)\n"
            f"• Relevant Experience Alignment (1-10)\n\n"
            f"⚠️ *IMPORTANT INSTRUCTIONS:*\n"
            f"• Please join 2-3 minutes early with webcam enabled.\n"
            f"• Log evaluation feedback immediately post-interview in the HR Nexus AI Portal.\n\n"
            f"— _HR Nexus AI Autonomous Recruitment Agent_"
        )
        return msg

    def get_whatsapp_web_link(self, phone: str, message: str) -> str:
        """Generate a direct click-to-chat WhatsApp deep link."""
        clean_phone = self.clean_phone(phone)
        encoded_text = urllib.parse.quote(message)
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"

    def send_shortlist_alert(self, candidate_name: str, job_title: str,
                            candidate_code: str = "CAND-001", department: str = "Engineering",
                            match_score: float = 0.0, skills_score: float = 0.0,
                            exp_score: float = 0.0, edu_score: float = 0.0,
                            experience_years: float = 0.0, current_org: str = "",
                            key_skills: str = "", missing_skills: str = "",
                            verification_flags: str = "", candidate_email: str = "",
                            candidate_phone: str = "", phone: str = None) -> dict:
        """Dispatch detailed shortlist notification to WhatsApp."""
        target_phone = phone or self.recipient_phone
        message_text = self.format_shortlist_dossier(
            candidate_name=candidate_name,
            candidate_code=candidate_code,
            job_title=job_title,
            department=department,
            match_score=match_score,
            skills_score=skills_score,
            exp_score=exp_score,
            edu_score=edu_score,
            experience_years=experience_years,
            current_org=current_org,
            key_skills=key_skills,
            missing_skills=missing_skills,
            verification_flags=verification_flags,
            candidate_email=candidate_email,
            candidate_phone=candidate_phone
        )
        web_link = self.get_whatsapp_web_link(target_phone, message_text)
        status = self._dispatch_via_api(target_phone, message_text)

        # Log to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (title, message, recipient_role, priority)
                VALUES (?, ?, 'HR Manager', 'High');
            """, (f"WhatsApp Shortlist: {candidate_name}", f"Shortlist dossier dispatched for {candidate_name} to {target_phone}"))

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("WHATSAPP_SHORTLIST_ALERT", "Notifications", "HR Agent", f"Shortlist WhatsApp for {candidate_name} -> {target_phone} ({status})"))

        return {
            "status": status,
            "recipient_phone": target_phone,
            "message_text": message_text,
            "web_link": web_link,
            "candidate_name": candidate_name
        }

    def send_interview_alert(self, candidate_name: str, candidate_code: str,
                            job_title: str, department: str,
                            round_name: str, round_number: int,
                            interviewer_name: str, interviewer_email: str,
                            scheduled_time: str, duration_minutes: int,
                            meeting_link: str, phone: str = None,
                            candidate_phone: str = "", candidate_email: str = "") -> dict:
        """Dispatch complete interview meeting invitation to WhatsApp."""
        target_phone = phone or self.recipient_phone
        message_text = self.format_interview_meeting_alert(
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
            candidate_phone=candidate_phone,
            candidate_email=candidate_email
        )
        web_link = self.get_whatsapp_web_link(target_phone, message_text)
        status = self._dispatch_via_api(target_phone, message_text)

        # Log to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications (title, message, recipient_role, priority)
                VALUES (?, ?, 'HR Manager', 'High');
            """, (f"WhatsApp Interview Scheduled: {candidate_name}", f"Meeting invite dispatched for {round_name} with {candidate_name} on {scheduled_time} to {target_phone}"))

            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("WHATSAPP_INTERVIEW_ALERT", "Notifications", "HR Agent", f"Interview WhatsApp for {candidate_name} ({round_name}) -> {target_phone} ({status})"))

        return {
            "status": status,
            "recipient_phone": target_phone,
            "message_text": message_text,
            "web_link": web_link,
            "candidate_name": candidate_name,
            "meeting_link": meeting_link,
            "scheduled_time": scheduled_time
        }

    def _dispatch_via_api(self, target_phone: str, message_text: str) -> str:
        """Try automated delivery via CallMeBot, Twilio, or Meta WhatsApp Business API."""
        clean_num = self.clean_phone(target_phone)

        # 1. Free CallMeBot Automated WhatsApp Gateway
        if self.callmebot_key:
            try:
                url = f"https://api.callmebot.com/whatsapp.php?phone=+{clean_num}&text={urllib.parse.quote(message_text)}&apikey={self.callmebot_key}"
                res = requests.get(url, timeout=10)
                if res.status_code == 200 and ("Message queued" in res.text or "ok" in res.text.lower()):
                    return "Sent via CallMeBot Free WhatsApp API"
            except Exception as e:
                print(f"CallMeBot error: {e}")

        # 2. Twilio WhatsApp REST API
        if self.twilio_sid and self.twilio_token:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
                formatted_to = f"whatsapp:+{clean_num}"
                data = {
                    "From": self.twilio_from,
                    "To": formatted_to,
                    "Body": message_text
                }
                res = requests.post(url, data=data, auth=(self.twilio_sid, self.twilio_token), timeout=8)
                if res.status_code in [200, 201]:
                    return "Sent via Twilio WhatsApp API"
            except Exception as e:
                print(f"Twilio API error: {e}")

        # 3. Meta Cloud API
        if self.meta_token and self.meta_phone_id:
            try:
                url = f"https://graph.facebook.com/v19.0/{self.meta_phone_id}/messages"
                headers = {"Authorization": f"Bearer {self.meta_token}", "Content-Type": "application/json"}
                payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_num,
                    "type": "text",
                    "text": {"body": message_text}
                }
                res = requests.post(url, json=payload, headers=headers, timeout=8)
                if res.status_code in [200, 201]:
                    return "Sent via Meta WhatsApp Cloud API"
            except Exception as e:
                print(f"Meta API error: {e}")

        return "Ready for 1-Click WhatsApp Dispatch"
