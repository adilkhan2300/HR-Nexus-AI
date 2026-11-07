"""
HR Nexus AI - View 8: Interview Management Agent & STAR Evaluation
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from agents.interview_agent import InterviewAgent
from database.connection import get_db
from services.notification_service import MultiChannelNotificationService

def render(user_role: str = "HR Manager"):
    st.markdown("### 📅 Interview Management Agent")
    st.markdown("Schedule multi-round interviews, generate role-specific STAR question banks, record multi-parameter evaluations, and synthesize panel feedback.")

    agent = InterviewAgent()

    tab_schedule, tab_feedback, tab_questions, tab_calendar = st.tabs([
        "🗓️ Schedule Interview", "📝 Record Evaluation & Feedback", "🤖 STAR Question Bank Generator", "📋 All Scheduled Interviews"
    ])

    # Fetch candidates eligible for interview (Shortlisted, Assessment, Interview Scheduled)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id as candidate_id, c.candidate_code, c.full_name, c.email, c.phone,
                   a.id as application_id, a.requisition_id, jr.title as job_title,
                   jr.department, jr.technical_skills
            FROM candidates c
            JOIN applications a ON c.id = a.candidate_id
            JOIN job_requisitions jr ON a.requisition_id = jr.id
            WHERE a.stage IN ('Shortlisted', 'Assessment', 'Interview Scheduled', 'Interview Completed', 'Selected');
        """)
        eligible_cands = [dict(r) for r in cursor.fetchall()]

    # TAB 1: SCHEDULE INTERVIEW
    with tab_schedule:
        st.markdown("##### 📌 Book a New Interview Round")
        if eligible_cands:
            cand_options = {f"{c['full_name']} - {c['job_title']} (App #{c['application_id']})": c for c in eligible_cands}
            sel_label = st.selectbox("Select Candidate:", list(cand_options.keys()))
            sel_c = cand_options[sel_label]

            col1, col2 = st.columns(2)
            with col1:
                round_name = st.selectbox("Interview Round:", [
                    "Technical Round 1", "System Architecture Round 2", "Case Study / Assessment Review",
                    "Behavioral & Culture Fit", "Executive / Leadership Round"
                ])
                round_num = st.number_input("Round Number", min_value=1, max_value=5, value=1)
                duration = st.selectbox("Duration (Minutes):", [30, 45, 60, 90], index=1)

            with col2:
                interviewer = st.selectbox("Assigned Interviewer:", ["David Chen (Engineering)", "Sarah Jenkins (HR)", "Elena Rostova (AI Lead)", "Marcus Vance (Product)"])
                interviewer_email = interviewer.split("(")[0].strip().lower().replace(" ", ".") + "@hrnexus.ai"
                sched_date = st.date_input("Interview Date:", value=datetime.now() + timedelta(days=2))
                sched_time = st.time_input("Interview Time:", value=datetime.strptime("14:00", "%H:%M").time())

            meet_link = st.text_input("Meeting Link (Google Meet / Teams):", value=f"https://meet.google.com/hrn-{sel_c['candidate_id']}01-meet")

            st.markdown("###### 📡 Multi-Channel Notification Settings (WhatsApp, SMS & Email)")
            col_notif1, col_notif2 = st.columns(2)
            with col_notif1:
                wa_phone = st.text_input(
                    "Recipient Phone Number (for WhatsApp & SMS):",
                    value=st.session_state.get("wa_phone_number", "+917888270396"),
                    help="Include country code, e.g. +917888270396"
                )
                st.session_state["wa_phone_number"] = wa_phone

                recip_email = st.text_input(
                    "Recipient Email Address (for Email Invitation):",
                    value=st.session_state.get("notif_email", "recruiter@hrnexus.ai"),
                    help="Email to receive the complete meeting agenda and calendar invite"
                )
                st.session_state["notif_email"] = recip_email

            with col_notif2:
                st.markdown("**Select Channels to Dispatch:**")
                send_wa_check = st.checkbox("💬 WhatsApp Meeting Dossier & Agenda", value=True)
                send_sms_check = st.checkbox("📱 SMS Meeting Alert (+91 7888270396)", value=True)
                send_email_check = st.checkbox("✉️ Email Invitation & Calendar Briefing", value=True)

            if st.button("Schedule Interview & Dispatch Notifications", type="primary"):
                dt_str = f"{sched_date} {sched_time.strftime('%H:%M:00')}"
                int_id = agent.schedule_interview(
                    application_id=sel_c['application_id'],
                    candidate_id=sel_c['candidate_id'],
                    requisition_id=sel_c['requisition_id'],
                    round_name=round_name,
                    round_number=round_num,
                    interviewer_name=interviewer.split("(")[0].strip(),
                    interviewer_email=interviewer_email,
                    scheduled_time=dt_str,
                    duration_minutes=duration,
                    meeting_link=meet_link
                )

                notif_service = MultiChannelNotificationService()
                multi_res = notif_service.send_interview_multi_channel(
                    candidate_name=sel_c['full_name'],
                    candidate_code=sel_c.get('candidate_code', f"CAND-{sel_c['candidate_id']:03d}"),
                    job_title=sel_c['job_title'],
                    department=sel_c.get('department', 'Engineering'),
                    round_name=round_name,
                    round_number=round_num,
                    interviewer_name=interviewer.split("(")[0].strip(),
                    interviewer_email=interviewer_email,
                    scheduled_time=dt_str,
                    duration_minutes=duration,
                    meeting_link=meet_link,
                    phone=wa_phone,
                    email=recip_email,
                    candidate_phone=sel_c.get('phone', ''),
                    candidate_email=sel_c.get('email', '')
                )
                st.session_state["last_interview_multi"] = multi_res
                st.session_state["last_scheduled_msg"] = f"Interview #{int_id} ({round_name}) successfully booked for {sel_c['full_name']} on {dt_str}!"

            if st.session_state.get("last_scheduled_msg"):
                st.success(st.session_state["last_scheduled_msg"])

            if st.session_state.get("last_interview_multi"):
                notif = st.session_state["last_interview_multi"]
                st.markdown("---")
                st.markdown("##### 📡 Multi-Channel Notifications Prepared & Dispatched:")

                c_wa, c_sms, c_em = st.columns(3)

                # 1. WhatsApp Card
                with c_wa:
                    st.markdown("**💬 WhatsApp Channel**")
                    st.caption(f"Status: `{notif['whatsapp']['status']}`")
                    st.link_button(
                        f"🚀 Open in WhatsApp ({notif['whatsapp']['recipient_phone']})",
                        url=notif['whatsapp']['web_link'],
                        use_container_width=True,
                        type="primary"
                    )
                    with st.expander("Preview WhatsApp Text"):
                        st.text(notif['whatsapp']['message_text'])

                # 2. SMS Card
                with c_sms:
                    st.markdown("**📱 SMS Channel**")
                    st.caption(f"Status: `{notif['sms']['status']}`")
                    st.link_button(
                        f"📲 Send Native SMS ({notif['sms']['recipient_phone']})",
                        url=notif['sms']['sms_link'],
                        use_container_width=True
                    )
                    with st.expander("Preview SMS Text"):
                        st.text(notif['sms']['message'])

                # 3. Email Card
                with c_em:
                    st.markdown("**✉️ Email Channel**")
                    st.caption(f"Status: `{notif['email']['status']}`")
                    st.link_button(
                        f"📧 Open in Mail App ({notif['email']['recipient_email']})",
                        url=notif['email']['mailto_link'],
                        use_container_width=True
                    )
                    with st.expander("Preview Email Draft"):
                        st.text(f"Subject: {notif['email']['subject']}\n\n{notif['email']['body']}")
        else:
            st.info("No candidates currently in Shortlisted or Interview stages.")

    # TAB 2: RECORD EVALUATION & FEEDBACK
    with tab_feedback:
        st.markdown("##### 📝 Structured Interview Evaluation Form")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.id, i.interview_code, i.round_name, i.interviewer_name, i.scheduled_time,
                       c.full_name, c.id as candidate_id
                FROM interviews i
                JOIN candidates c ON i.candidate_id = c.id
                WHERE i.status = 'Scheduled'
                ORDER BY i.scheduled_time ASC;
            """)
            sched_ints = [dict(r) for r in cursor.fetchall()]

        if sched_ints:
            int_map = {f"{r['interview_code']} - {r['full_name']} ({r['round_name']})": r for r in sched_ints}
            sel_int_label = st.selectbox("Select Scheduled Interview to Score:", list(int_map.keys()))
            target_int = int_map[sel_int_label]

            st.markdown(f"**Candidate:** {target_int['full_name']} | **Round:** {target_int['round_name']}")

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                t_score = st.slider("Technical Mastery (1-10)", 1.0, 10.0, 8.5, 0.5)
            with c2:
                c_score = st.slider("Communication (1-10)", 1.0, 10.0, 8.0, 0.5)
            with c3:
                p_score = st.slider("Problem Solving (1-10)", 1.0, 10.0, 8.5, 0.5)
            with c4:
                comp_score = st.slider("Role Competency (1-10)", 1.0, 10.0, 8.0, 0.5)
            with c5:
                e_score = st.slider("Experience Match (1-10)", 1.0, 10.0, 9.0, 0.5)

            strengths = st.text_area("Key Strengths", "Demonstrated clear architectural reasoning and deep knowledge of asynchronous backend workflows.")
            weaknesses = st.text_area("Areas for Development", "Could be more proactive in clarifying ambiguous non-functional constraints.")
            comments = st.text_area("Detailed Interviewer Comments", "Strong performance on code design question. Would thrive in our core platform team.")
            rec = st.selectbox("Interviewer Recommendation:", ["Strong Hire", "Hire", "Hold", "Reject"], index=1)

            if st.button("Submit Evaluation Form"):
                agent.submit_feedback(
                    interview_id=target_int['id'],
                    interviewer_name=target_int['interviewer_name'],
                    tech_score=t_score,
                    comm_score=c_score,
                    prob_score=p_score,
                    comp_score=comp_score,
                    exp_score=e_score,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    comments=comments,
                    recommendation=rec
                )
                st.success(f"Feedback submitted successfully for {target_int['full_name']}! Interview marked Completed.")
                st.rerun()
        else:
            st.info("No interviews currently awaiting feedback submission.")

    # TAB 3: STAR QUESTION GENERATOR
    with tab_questions:
        st.markdown("##### 🤖 Role-Specific STAR Behavioral & Technical Question Bank")
        target_role = st.text_input("Enter Target Role / Skill Area:", "Lead Business Analyst")
        target_skills = st.text_input("Target Skills:", "BRD/FRD Drafting, Stakeholder Management, BPMN, Agile")
        q_round = st.selectbox("Target Round Type:", ["Technical & Architecture", "Behavioral (STAR)", "Executive Leadership"])

        if st.button("Generate Question Bank"):
            with st.spinner("AI Interview Architect creating structured STAR questions..."):
                q_bank = agent.generate_interview_questions(target_role, target_skills, q_round)
            st.markdown(q_bank["generated_text"])

    # TAB 4: ALL SCHEDULED INTERVIEWS
    with tab_calendar:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.interview_code, c.full_name as candidate, jr.title as role,
                       i.round_name, i.interviewer_name, i.scheduled_time, i.duration_minutes,
                       i.meeting_link, i.status
                FROM interviews i
                JOIN candidates c ON i.candidate_id = c.id
                JOIN job_requisitions jr ON i.requisition_id = jr.id
                ORDER BY i.scheduled_time DESC;
            """)
            all_ints = [dict(r) for r in cursor.fetchall()]

        if all_ints:
            df_ints = pd.DataFrame(all_ints)
            st.dataframe(df_ints, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### 📡 Quick Multi-Channel Reminder Dispatch (WhatsApp, SMS & Email)")
            int_pick_map = {f"{r['interview_code']} - {r['candidate']} ({r['round_name']} on {r['scheduled_time']})": r for r in all_ints}
            sel_reminder_int = st.selectbox("Select Scheduled Interview to Send Reminder:", list(int_pick_map.keys()))
            picked_int = int_pick_map[sel_reminder_int]

            col_rem_p, col_rem_e, col_rem_b = st.columns([1.2, 1.2, 1])
            with col_rem_p:
                rem_phone = st.text_input("Recipient Phone (WhatsApp & SMS):", value=st.session_state.get("wa_phone_number", "+917888270396"), key="rem_phone_input")
            with col_rem_e:
                rem_email = st.text_input("Recipient Email:", value=st.session_state.get("notif_email", "recruiter@hrnexus.ai"), key="rem_email_input")
            with col_rem_b:
                st.write("")
                st.write("")
                if st.button("🚀 Dispatch Multi-Channel Reminder", type="primary"):
                    notif_service = MultiChannelNotificationService()
                    rem_multi = notif_service.send_interview_multi_channel(
                        candidate_name=picked_int['candidate'],
                        candidate_code=picked_int.get('interview_code', 'INT-001'),
                        job_title=picked_int.get('role', 'Candidate'),
                        department='Engineering',
                        round_name=picked_int.get('round_name', 'Technical Round'),
                        round_number=1,
                        interviewer_name=picked_int.get('interviewer_name', 'HR Panel'),
                        interviewer_email="interviewer@hrnexus.ai",
                        scheduled_time=picked_int.get('scheduled_time', ''),
                        duration_minutes=picked_int.get('duration_minutes', 45),
                        meeting_link=picked_int.get('meeting_link', 'https://meet.google.com'),
                        phone=rem_phone,
                        email=rem_email
                    )
                    st.session_state["last_rem_multi"] = rem_multi

            if st.session_state.get("last_rem_multi"):
                rm = st.session_state["last_rem_multi"]
                col_rwa, col_rsms, col_rem = st.columns(3)
                with col_rwa:
                    st.link_button(f"💬 Send WhatsApp ({rm['whatsapp']['recipient_phone']})", url=rm['whatsapp']['web_link'], type="primary", use_container_width=True)
                with col_rsms:
                    st.link_button(f"📱 Send SMS ({rm['sms']['recipient_phone']})", url=rm['sms']['sms_link'], use_container_width=True)
                with col_rem:
                    st.link_button(f"✉️ Send Email ({rm['email']['recipient_email']})", url=rm['email']['mailto_link'], use_container_width=True)
        else:
            st.info("No interview records found.")


