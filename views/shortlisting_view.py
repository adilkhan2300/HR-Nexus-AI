"""
HR Nexus AI - View 7: Intelligent Candidate Shortlisting & Comparative Matrix
"""
import streamlit as st
import pandas as pd
from agents.shortlisting_agent import ShortlistingAgent
from database.connection import get_db
from services.notification_service import MultiChannelNotificationService

def render(user_role: str = "HR Manager"):
    st.markdown("### 🏆 Intelligent Candidate Shortlisting")
    st.markdown("Rank, compare, and shortlist high-potential talent using multi-dimensional qualifications, skill gap analytics, and human sign-off gates.")

    agent = ShortlistingAgent()

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, requisition_code, title FROM job_requisitions WHERE approval_status = 'Approved';")
        req_rows = cursor.fetchall()

    req_options = {f"{r['requisition_code']} - {r['title']}": r['id'] for r in req_rows}
    sel_req_title = st.selectbox("Select Target Job Requisition:", ["All Openings"] + list(req_options.keys()))
    sel_req_id = req_options.get(sel_req_title) if sel_req_title != "All Openings" else None

    # Filter controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        min_score = st.slider("Minimum Match Score (%)", min_value=0, max_value=100, value=70)
    with col_f2:
        stage_filter = st.selectbox("Pipeline Stage:", ["All Stages", "Applied", "Resume Screening", "Shortlisted", "Assessment", "Interview Scheduled"])
    with col_f3:
        min_exp = st.number_input("Minimum Experience (Years)", min_value=0.0, max_value=20.0, value=2.0, step=0.5)

    ranked_candidates = agent.get_ranked_candidates(requisition_id=sel_req_id, min_score=float(min_score), stage_filter=stage_filter)
    # Further filter by min_exp
    ranked_candidates = [c for c in ranked_candidates if c['total_experience_years'] >= min_exp]

    tab_rank, tab_compare = st.tabs(["🎖️ Candidate Rankings", "⚖️ Multi-Candidate Side-by-Side Comparison"])

    # TAB 1: CANDIDATE RANKINGS
    with tab_rank:
        st.markdown(f"Found **{len(ranked_candidates)}** qualified candidates matching your criteria:")

        if ranked_candidates:
            df = pd.DataFrame(ranked_candidates)
            cols_show = ['full_name', 'job_title', 'overall_match_score', 'total_experience_years', 'highest_education', 'current_organization', 'stage', 'recommendation']
            st.dataframe(df[cols_show], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("##### ✍️ Action: Approve Candidates for Shortlisting & Trigger WhatsApp Alerts")

            col_sel_cand, col_wa_conf = st.columns([1.5, 1.2])
            with col_sel_cand:
                shortlist_candidates = st.multiselect(
                    "Select candidates to officially move to 'Shortlisted' stage:",
                    [f"{c['full_name']} (Score: {c['overall_match_score']}%, App #{c['application_id']})" for c in ranked_candidates]
                )
            with col_wa_conf:
                st.markdown("**📡 Multi-Channel Notification Settings:**")
                wa_phone = st.text_input(
                    "Recipient Phone (for WhatsApp & SMS):",
                    value=st.session_state.get("wa_phone_number", "+917888270396"),
                    help="e.g. +917888270396"
                )
                st.session_state["wa_phone_number"] = wa_phone

                recip_email = st.text_input(
                    "Recipient Email:",
                    value=st.session_state.get("notif_email", "recruiter@hrnexus.ai"),
                    help="e.g. recruiter@hrnexus.ai"
                )
                st.session_state["notif_email"] = recip_email

                send_wa_check = st.checkbox("💬 Send WhatsApp Dossier", value=True)
                send_sms_check = st.checkbox("📱 Send SMS Alert (+91 7888270396)", value=True)
                send_em_check = st.checkbox("✉️ Send Shortlist Email", value=True)

            if st.button("✅ Approve Selected for Shortlist", type="primary") and shortlist_candidates:
                notif_service = MultiChannelNotificationService()
                count_moved = 0
                dispatched_alerts = []

                for item in shortlist_candidates:
                    app_id = int(item.split("App #")[1].replace(")", ""))
                    agent.update_candidate_stage(app_id, "Shortlisted", notes="Approved during Shortlisting Review", approved_by=user_role)
                    count_moved += 1

                    # Find candidate details for alert
                    cand_obj = next((c for c in ranked_candidates if c['application_id'] == app_id), None)
                    if cand_obj:
                        alert_multi = notif_service.send_shortlist_multi_channel(
                            candidate_name=cand_obj['full_name'],
                            candidate_code=cand_obj.get('candidate_code', f"CAND-{cand_obj['candidate_id']:03d}"),
                            job_title=cand_obj['job_title'],
                            department=cand_obj.get('department', 'Engineering'),
                            match_score=cand_obj.get('overall_match_score', 0),
                            skills_score=cand_obj.get('skills_match_score', 0),
                            exp_score=cand_obj.get('experience_match_score', 0),
                            edu_score=cand_obj.get('education_match_score', 0),
                            experience_years=cand_obj.get('total_experience_years', 0),
                            current_org=cand_obj.get('current_organization', ''),
                            key_skills=cand_obj.get('matching_skills', ''),
                            missing_skills=cand_obj.get('missing_skills', 'None'),
                            phone=wa_phone,
                            email=recip_email
                        )
                        dispatched_alerts.append(alert_multi)

                st.session_state["last_shortlist_multi"] = dispatched_alerts
                st.success(f"🎉 Successfully shortlisted {count_moved} candidate(s)! Multi-channel notifications generated.")

            # Show Multi-Channel Notification Dispatch Cards
            if "last_shortlist_multi" in st.session_state and st.session_state["last_shortlist_multi"]:
                st.markdown("---")
                st.markdown("##### 📡 Multi-Channel Shortlist Notifications:")
                for alert in st.session_state["last_shortlist_multi"]:
                    st.markdown(f"**Candidate:** `{alert['candidate_name']}`")
                    c_wa, c_sms, c_em = st.columns(3)
                    with c_wa:
                        st.link_button(
                            f"💬 WhatsApp Dossier ({alert['whatsapp']['recipient_phone']})",
                            url=alert['whatsapp']['web_link'],
                            type="primary",
                            use_container_width=True
                        )
                    with c_sms:
                        st.link_button(
                            f"📱 Send SMS ({alert['sms']['recipient_phone']})",
                            url=alert['sms']['sms_link'],
                            use_container_width=True
                        )
                    with c_em:
                        st.link_button(
                            f"✉️ Send Email ({alert['email']['recipient_email']})",
                            url=alert['email']['mailto_link'],
                            use_container_width=True
                        )
        else:
            st.info("No candidates match the selected filters. Try lowering the match score slider.")

    # TAB 2: MULTI-CANDIDATE COMPARISON
    with tab_compare:
        st.markdown("##### ⚖️ Side-by-Side Candidate Matrix & Skill Gap Analysis")
        if ranked_candidates:
            cand_select_map = {f"{c['full_name']} ({c['current_designation']} - {c['total_experience_years']} yrs)": c['candidate_id'] for c in ranked_candidates}
            selected_to_compare = st.multiselect(
                "Select 2 to 4 candidates to compare:",
                list(cand_select_map.keys()),
                default=list(cand_select_map.keys())[:min(3, len(cand_select_map))]
            )

            if len(selected_to_compare) >= 2:
                cids = [cand_select_map[name] for name in selected_to_compare]
                cmp_data = agent.compare_candidates(cids, sel_req_id or 1)

                st.info(f"**AI Comparative Analysis:** {cmp_data['summary']}")

                # Render Comparison Grid using unindented HTML
                c_cols = st.columns(len(cmp_data['candidates']))
                for idx, c in enumerate(cmp_data['candidates']):
                    with c_cols[idx]:
                        score_val = c.get('overall_match_score', 0)
                        card_html = (
                            f'<div style="background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 14px; margin-bottom: 10px; color: #f8fafc;">'
                            f'<h4 style="margin: 0; color: #60a5fa; font-size: 1.1rem;">{c["full_name"]}</h4>'
                            f'<span style="font-size: 0.8rem; color: #94a3b8;">{c["current_designation"]}</span>'
                            f'<div style="font-size: 1.4rem; font-weight: 800; color: #34d399; margin: 8px 0;">⭐ {score_val}% Match</div>'
                            f'<hr style="border: none; border-top: 1px solid #334155; margin: 8px 0;"/>'
                            f'<p style="font-size: 0.82rem; margin: 4px 0; color: #cbd5e1;"><b>Experience:</b> {c["total_experience_years"]} Years</p>'
                            f'<p style="font-size: 0.82rem; margin: 4px 0; color: #cbd5e1;"><b>Education:</b> {c["highest_education"]}</p>'
                            f'<p style="font-size: 0.82rem; margin: 4px 0; color: #cbd5e1;"><b>Organization:</b> {c["current_organization"]}</p>'
                            f'<p style="font-size: 0.82rem; margin: 4px 0; color: #cbd5e1;"><b>Notice Period:</b> {c["notice_period_days"]} Days</p>'
                            f'<p style="font-size: 0.82rem; margin: 4px 0; color: #cbd5e1;"><b>Skills Score:</b> {c.get("skills_match_score", 0)}%</p>'
                            f'<div style="background: #0f172a; padding: 6px; border-radius: 6px; font-size: 0.75rem; margin-top: 6px; color: #93c5fd;">'
                            f'<b>Key Matches:</b> {str(c.get("matching_skills", "N/A"))[:50]}...'
                            f'</div>'
                            f'<div style="background: #0f172a; padding: 6px; border-radius: 6px; font-size: 0.75rem; margin-top: 6px; color: #fca5a5;">'
                            f'<b>Skill Gaps:</b> {c.get("missing_skills", "None")}'
                            f'</div>'
                            f'</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.warning("Please select at least 2 candidates to compare side-by-side.")
        else:
            st.info("No candidates available for comparison.")

