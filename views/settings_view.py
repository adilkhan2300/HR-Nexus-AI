"""
HR Nexus AI - View 15: Settings, Role Management & System Audit Logs
"""
import os
import streamlit as st
import pandas as pd
from database.connection import get_db, init_db
from database.seed_data import seed_all_data
from database.seed_50_candidates import seed_50_candidates
from services.auth_service import AuthService
from services.notification_service import MultiChannelNotificationService
from config import DATABASE_PATH

def render(user_role: str = "HR Manager"):
    st.markdown("### ⚙️ System Settings, Security & Audit Logs")
    st.markdown("Manage AI provider keys, multi-channel notifications (WhatsApp, SMS, Email), role permissions, security, and audit logs.")

    tab_api, tab_wa, tab_users, tab_audit, tab_reset = st.tabs([
        "🔑 AI Provider Configuration", "📡 Multi-Channel Notifications", "👥 User Roles & Permissions", "📜 System Audit Logs", "🔄 Reset / Re-Seed Database"
    ])

    # TAB 1: AI PROVIDER KEYS
    with tab_api:
        st.markdown("##### 🔌 AI Model Integration & Demo Mode")
        st.info("💡 **Dual Mode Support**: If API keys are not supplied, HR Nexus AI automatically operates in intelligent **Demo Mode** using built-in deterministic heuristics, regex parsers, and policy synthesis engines.")

        current_openai = os.getenv("OPENAI_API_KEY", "")
        current_gemini = os.getenv("GEMINI_API_KEY", "")

        with st.form("api_key_form"):
            openai_input = st.text_input("OpenAI API Key (Optional)", value=current_openai, type="password", placeholder="sk-...")
            gemini_input = st.text_input("Google Gemini API Key (Optional)", value=current_gemini, type="password", placeholder="AIzaSy...")
            provider_choice = st.selectbox("Preferred AI Mode:", ["auto (Use live API if available, else Demo Mode)", "demo (Enforce offline Demo Mode)"])

            saved = st.form_submit_button("Save Provider Settings")
            if saved:
                if openai_input:
                    os.environ["OPENAI_API_KEY"] = openai_input
                if gemini_input:
                    os.environ["GEMINI_API_KEY"] = gemini_input
                os.environ["AI_PROVIDER"] = "demo" if "demo" in provider_choice else "auto"
                st.success("API configuration updated successfully!")
                st.rerun()

    # TAB 2: MULTI-CHANNEL NOTIFICATIONS (WHATSAPP, SMS & EMAIL)
    with tab_wa:
        st.markdown("##### 📡 Multi-Channel Notification Configuration (WhatsApp, SMS & Email)")
        st.markdown("Configure direct dispatches for candidate shortlisting dossiers and interview invitations across **WhatsApp**, **SMS**, and **Email**.")

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            cfg_user_phone = st.text_input(
                "Recipient Phone (for WhatsApp & SMS):",
                value=os.getenv("WHATSAPP_RECIPIENT_PHONE", st.session_state.get("wa_phone_number", "+917888270396")),
                help="Include country code, e.g. +917888270396"
            )
            cfg_hr_phone = st.text_input(
                "HR Department Phone (Group):",
                value=os.getenv("WHATSAPP_HR_PHONE", st.session_state.get("wa_hr_phone", "+917888270396")),
                help="Used for central HR notifications"
            )
            cfg_user_email = st.text_input(
                "Recipient Email Address:",
                value=os.getenv("NOTIFICATION_EMAIL", st.session_state.get("notif_email", "recruiter@hrnexus.ai")),
                help="Used for interview invitations and shortlist emails"
            )
        with col_w2:
            st.info("""
            💡 **Zero-Key 1-Click Launch Ready**:
            • **WhatsApp**: Direct `wa.me` links pre-fill message with Google Meet link & agenda.
            • **SMS**: Direct `sms:` deep-links launch your native SMS messenger app.
            • **Email**: Direct `mailto:` deep-links launch Outlook / Gmail with subject & body pre-filled.
            """)

        with st.expander("🛠️ Optional Background Push Gateways (Twilio, CallMeBot, Fast2SMS, SMTP)"):
            st.markdown("**1. Email Gateway (SMTP / Gmail / Outlook)**")
            c_smtp1, c_smtp2 = st.columns(2)
            with c_smtp1:
                smtp_host = st.text_input("SMTP Server Host:", value=os.getenv("SMTP_HOST", "smtp.gmail.com"))
                smtp_user = st.text_input("SMTP Username / Email:", value=os.getenv("SMTP_USER", ""))
            with c_smtp2:
                smtp_port = st.number_input("SMTP Port:", value=int(os.getenv("SMTP_PORT", 587)))
                smtp_pass = st.text_input("SMTP App Password:", value=os.getenv("SMTP_PASSWORD", ""), type="password")

            st.markdown("---")
            st.markdown("**2. SMS Gateway (Fast2SMS for India or Twilio SMS)**")
            c_sms1, c_sms2 = st.columns(2)
            with c_sms1:
                f2s_key = st.text_input("Fast2SMS API Key (for India):", value=os.getenv("FAST2SMS_API_KEY", ""))
            with c_sms2:
                tw_sms_num = st.text_input("Twilio SMS Sender Number:", value=os.getenv("TWILIO_SMS_NUMBER", ""))

            st.markdown("---")
            st.markdown("**3. WhatsApp Background Push (CallMeBot or Twilio)**")
            cmb_key = st.text_input("CallMeBot Free API Key:", value=os.getenv("CALLMEBOT_API_KEY", ""), help="Message 'I allow callmebot to send me messages' to +34 644 44 47 62 to get your free key")
            tw_sid = st.text_input("Twilio Account SID:", value=os.getenv("TWILIO_ACCOUNT_SID", ""))
            tw_token = st.text_input("Twilio Auth Token:", value=os.getenv("TWILIO_AUTH_TOKEN", ""), type="password")

        if st.button("💾 Save Multi-Channel Configuration"):
            os.environ["WHATSAPP_RECIPIENT_PHONE"] = cfg_user_phone
            os.environ["WHATSAPP_HR_PHONE"] = cfg_hr_phone
            os.environ["NOTIFICATION_EMAIL"] = cfg_user_email
            if smtp_host: os.environ["SMTP_HOST"] = smtp_host
            os.environ["SMTP_PORT"] = str(smtp_port)
            if smtp_user: os.environ["SMTP_USER"] = smtp_user
            if smtp_pass: os.environ["SMTP_PASSWORD"] = smtp_pass
            if f2s_key: os.environ["FAST2SMS_API_KEY"] = f2s_key
            if tw_sms_num: os.environ["TWILIO_SMS_NUMBER"] = tw_sms_num
            if cmb_key: os.environ["CALLMEBOT_API_KEY"] = cmb_key
            if tw_sid: os.environ["TWILIO_ACCOUNT_SID"] = tw_sid
            if tw_token: os.environ["TWILIO_AUTH_TOKEN"] = tw_token

            st.session_state["wa_phone_number"] = cfg_user_phone
            st.session_state["wa_hr_phone"] = cfg_hr_phone
            st.session_state["notif_email"] = cfg_user_email
            st.success("Multi-channel configuration successfully saved!")

        st.markdown("---")
        st.markdown("##### 🧪 Test Multi-Channel Dispatch (WhatsApp, SMS & Email)")
        if st.button("🚀 Send Test Dispatch Across All 3 Channels"):
            notif_service = MultiChannelNotificationService()
            test_res = notif_service.send_interview_multi_channel(
                candidate_name="Alex Rivera",
                candidate_code="CAND-016",
                job_title="Senior Python Developer",
                department="Engineering",
                round_name="Technical Round 1",
                round_number=1,
                interviewer_name="David Chen",
                interviewer_email="david.chen@hrnexus.ai",
                scheduled_time="2026-11-09 14:00:00",
                duration_minutes=45,
                meeting_link="https://meet.google.com/hrn-2101-meet",
                phone=cfg_user_phone,
                email=cfg_user_email
            )
            st.session_state["test_multi_res"] = test_res

        if st.session_state.get("test_multi_res"):
            tm = st.session_state["test_multi_res"]
            st.success("Multi-channel test pack prepared!")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**💬 WhatsApp**")
                st.caption(f"Status: `{tm['whatsapp']['status']}`")
                st.link_button(f"Open WhatsApp ({tm['whatsapp']['recipient_phone']})", url=tm['whatsapp']['web_link'], type="primary", use_container_width=True)
            with c2:
                st.markdown("**📱 SMS**")
                st.caption(f"Status: `{tm['sms']['status']}`")
                st.link_button(f"Send SMS ({tm['sms']['recipient_phone']})", url=tm['sms']['sms_link'], use_container_width=True)
            with c3:
                st.markdown("**✉️ Email**")
                st.caption(f"Status: `{tm['email']['status']}`")
                st.link_button(f"Open Mail Draft ({tm['email']['recipient_email']})", url=tm['email']['mailto_link'], use_container_width=True)

    # TAB 3: USER ROLES & ACCESS CONTROL
    with tab_users:
        st.markdown("##### 👥 System User Directory")
        users = AuthService.get_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)

        st.markdown("##### 🛡️ Role Permission Matrix")
        perm_data = [
            {"Role": "Admin", "Requisition Control": "Full (Create/Approve)", "Resume Screening": "Full Access", "Offers": "Create & Sign", "Onboarding": "Full Access", "Analytics": "Full Access", "Salary Info": "Visible"},
            {"Role": "HR Manager", "Requisition Control": "Full (Create/Approve)", "Resume Screening": "Full Access", "Offers": "Create & Sign", "Onboarding": "Full Access", "Analytics": "Full Access", "Salary Info": "Visible"},
            {"Role": "Interviewer / Dept Manager", "Requisition Control": "View Assigned", "Resume Screening": "View Shortlisted", "Offers": "Restricted", "Onboarding": "Task Update Only", "Analytics": "Restricted", "Salary Info": "Hidden / Redacted"}
        ]
        st.dataframe(pd.DataFrame(perm_data), use_container_width=True, hide_index=True)

    # TAB 3: AUDIT LOGS
    with tab_audit:
        st.markdown("##### 📜 Immutable System Activity Audit Trail")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, user_action, module, performed_by, details FROM audit_logs ORDER BY id DESC LIMIT 50;")
            logs = [dict(r) for r in cursor.fetchall()]

        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        else:
            st.info("No audit logs recorded yet.")

    # TAB 5: RESET / RE-SEED
    with tab_reset:
        st.markdown("##### ⚠️ Reset and Seed Database")
        st.warning("This operation will reset all 19 database tables and restore the baseline demo data (5 jobs, 50 candidates across all 12 stages, 10 interviews, 5 employees, 10 onboarding tasks, 5 HR policies).")

        if st.button("🔄 Reset & Seed Fresh Sample Data", type="primary"):
            if DATABASE_PATH.exists():
                try:
                    os.remove(DATABASE_PATH)
                except Exception:
                    pass
            seed_all_data()
            seed_50_candidates()
            st.success("Database restored to pristine 50-candidate sample state!")
            st.rerun()

