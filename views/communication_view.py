"""
HR Nexus AI - View 9: Candidate Communication Center
"""
import streamlit as st
import pandas as pd
from agents.communication_agent import CommunicationAgent, COMMUNICATION_TEMPLATES
from database.connection import get_db
from services.notification_service import MultiChannelNotificationService

def render(user_role: str = "HR Manager"):
    st.markdown("### ✉️ Candidate Communication Center")
    st.markdown("Draft, customize, approve, and dispatch personalized milestone emails across the complete applicant lifecycle.")

    comm_agent = CommunicationAgent()

    tab_compose, tab_history, tab_templates = st.tabs(["✍️ Compose & Dispatch", "📬 Communication History", "📑 Template Library"])

    # Fetch candidate list
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.full_name, c.email, c.phone, a.id as application_id, jr.title as job_title, a.stage
            FROM candidates c
            JOIN applications a ON c.id = a.candidate_id
            JOIN job_requisitions jr ON a.requisition_id = jr.id
            ORDER BY c.full_name ASC;
        """)
        cands = [dict(r) for r in cursor.fetchall()]

    # TAB 1: COMPOSE & DISPATCH
    with tab_compose:
        col_c, col_t = st.columns(2)
        with col_c:
            cand_map = {f"{c['full_name']} ({c['job_title']} - {c['stage']})": c for c in cands}
            sel_cand_label = st.selectbox("Select Candidate:", list(cand_map.keys()))
            sel_cand = cand_map[sel_cand_label]
        with col_t:
            template_name = st.selectbox("Select Communication Template:", list(COMMUNICATION_TEMPLATES.keys()))

        # Pre-fill context
        context = {
            "candidate_name": sel_cand["full_name"],
            "recipient_email": sel_cand["email"],
            "job_title": sel_cand["job_title"],
            "candidate_id": sel_cand["id"],
            "sender_name": "Sarah Jenkins, HR Operations",
            "round_name": "Round 1 Technical Discussion",
            "interviewer_name": "David Chen",
            "scheduled_time": "March 10, 2026 at 2:00 PM EST",
            "meeting_link": "https://meet.google.com/hrn-tech-eval",
            "duration_minutes": "45",
            "annual_ctc": 125000,
            "currency": "USD",
            "joining_date": "April 1, 2026",
            "work_location": "Austin, TX (Hybrid)",
            "offer_deadline": "March 20, 2026"
        }

        rendered = comm_agent.get_template(template_name, context)

        st.markdown("##### 📝 Review & Edit Email Draft (Human-in-the-Loop)")
        subject_edited = st.text_input("Email Subject Line:", value=rendered["subject"])
        body_edited = st.text_area("Email Body Text:", value=rendered["body"], height=240)

        c_send, c_copy = st.columns(2)
        with c_send:
            if st.button("🚀 Approve & Dispatch Email", type="primary"):
                comm_id = comm_agent.save_communication(
                    candidate_id=sel_cand["id"],
                    application_id=sel_cand["application_id"],
                    comm_type=template_name,
                    subject=subject_edited,
                    body=body_edited,
                    sender="Sarah Jenkins",
                    recipient_email=sel_cand["email"],
                    status="Sent",
                    approved_by=user_role
                )
                st.success(f"Email successfully dispatched to {sel_cand['email']}! (Logged as Comm ID #{comm_id})")
                st.rerun()

        with c_copy:
            st.download_button(
                label="📥 Download Email Text (.txt)",
                data=f"Subject: {subject_edited}\nTo: {sel_cand['email']}\n\n{body_edited}",
                file_name=f"Email_{template_name.replace(' ', '_')}_{sel_cand['full_name']}.txt",
                mime="text/plain"
            )

        st.markdown("---")
        st.markdown("##### 📡 1-Click Multi-Channel Immediate Launch:")
        notif_srv = MultiChannelNotificationService()
        mailto_url = notif_srv.get_mailto_link(sel_cand['email'], subject_edited, body_edited)
        cand_phone = sel_cand.get('phone') or st.session_state.get('wa_phone_number', '+917888270396')
        wa_url = notif_srv.wa_service.get_whatsapp_web_link(cand_phone, f"*{subject_edited}*\n\n{body_edited}")
        sms_url = notif_srv.get_sms_link(cand_phone, f"{subject_edited}: {body_edited[:130]}...")

        c_d1, c_d2, c_d3 = st.columns(3)
        with c_d1:
            st.link_button(f"📧 Open in Mail App ({sel_cand['email']})", url=mailto_url, use_container_width=True, type="primary")
        with c_d2:
            st.link_button(f"💬 Send in WhatsApp ({cand_phone})", url=wa_url, use_container_width=True)
        with c_d3:
            st.link_button(f"📱 Send in SMS ({cand_phone})", url=sms_url, use_container_width=True)

    # TAB 2: COMMUNICATION HISTORY
    with tab_history:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT com.id, c.full_name, com.recipient_email, com.communication_type,
                       com.subject, com.status, com.approved_by, com.sent_at
                FROM communications com
                JOIN candidates c ON com.candidate_id = c.id
                ORDER BY com.id DESC;
            """)
            hist = [dict(r) for r in cursor.fetchall()]

        if hist:
            df_hist = pd.DataFrame(hist)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("No communications logged yet.")

    # TAB 3: TEMPLATE LIBRARY
    with tab_templates:
        st.markdown("##### 📚 All Standard Communication Templates")
        for t_name, t_data in COMMUNICATION_TEMPLATES.items():
            with st.expander(f"✉️ {t_name}"):
                st.write(f"**Subject Template:** `{t_data['subject']}`")
                st.text(t_data['body'])

