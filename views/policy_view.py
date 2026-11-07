"""
HR Nexus AI - View 13: HR Policy & SOP Knowledge Agent (RAG)
"""
import streamlit as st
import pandas as pd
from agents.policy_rag_agent import PolicyRAGAgent
from database.connection import get_db
from services.resume_parser import extract_text_from_file

def render(user_role: str = "HR Manager"):
    st.markdown("### 📚 HR Policy and SOP Knowledge Agent")
    st.markdown("Ask natural language compliance, benefit, and policy questions. The agent leverages Retrieval-Augmented Generation (RAG) to provide exact, verifiable citations from company handbooks.")

    rag_agent = PolicyRAGAgent()

    tab_qa, tab_repository, tab_upload = st.tabs(["💬 Ask Knowledge Agent", "📖 Policy Repository", "📤 Upload New Policy Document"])

    # TAB 1: RAG Q&A
    with tab_qa:
        st.markdown("##### 💡 Suggested Questions")
        q_cols = st.columns(3)
        with q_cols[0]:
            if st.button("🌴 'What is the company's leave policy?'"):
                st.session_state.policy_query = "What is the company's leave policy?"
            if st.button("💻 'Who approves laptop allocation?'"):
                st.session_state.policy_query = "Who approves laptop allocation?"
        with q_cols[1]:
            if st.button("📋 'What documents are required during onboarding?'"):
                st.session_state.policy_query = "What documents are required during onboarding?"
            if st.button("⏰ 'What are core working hours and hybrid rules?'"):
                st.session_state.policy_query = "What are core working hours and hybrid rules?"
        with q_cols[2]:
            if st.button("⚖️ 'Explain the recruitment approval process.'"):
                st.session_state.policy_query = "Explain the recruitment approval process."
            if st.button("🛡️ 'What is the policy on conflict of interest?'"):
                st.session_state.policy_query = "What is the policy on conflict of interest?"

        user_query = st.text_input("Enter your policy question:", value=st.session_state.pop("policy_query", ""), placeholder="e.g. How many sick leave days are provided per year?")

        if user_query:
            with st.spinner("Knowledge Agent scanning policy library and cross-referencing sections..."):
                res = rag_agent.answer_query(user_query)

            st.markdown("##### 📌 Verifiable Policy Response:")
            st.info(res["answer"])

            if res["citations"]:
                st.markdown("##### 🔍 Source Document Citations:")
                for c in res["citations"]:
                    st.markdown(f"- **{c['policy']}** (*{c['category']}*)\n  > \"{c['snippet']}\"")

    # TAB 2: POLICY REPOSITORY
    with tab_repository:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, version, summary, effective_date FROM hr_policies;")
            policies = [dict(r) for r in cursor.fetchall()]

        if policies:
            st.dataframe(pd.DataFrame(policies), use_container_width=True, hide_index=True)

            sel_pol_title = st.selectbox("Inspect Full Policy Text:", [p['title'] for p in policies])
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT content FROM hr_policies WHERE title = ?;", (sel_pol_title,))
                row = cursor.fetchone()
                if row:
                    st.text_area("Full Document Content", row['content'], height=280)
        else:
            st.info("No policy documents found.")

    # TAB 3: UPLOAD POLICY
    with tab_upload:
        st.markdown("##### 📤 Ingest Policy Document (PDF, DOCX, TXT)")
        with st.form("new_policy_form"):
            p_title = st.text_input("Policy Title *", value="Travel and Expense Reimbursement Policy")
            p_cat = st.selectbox("Category *", ["Leave & Attendance", "Ethics & Governance", "Operations", "Recruitment", "Benefits & Compensation", "General"])
            p_ver = st.text_input("Document Version", value="1.0")
            p_file = st.file_uploader("Upload Policy Document", type=["pdf", "docx", "txt"])
            p_manual_text = st.text_area("Or Paste Policy Text Directly:", height=150)

            p_submit = st.form_submit_button("Ingest Policy into Repository")
            if p_submit:
                content = ""
                if p_file:
                    content = extract_text_from_file(p_file, p_file.name)
                elif p_manual_text.strip():
                    content = p_manual_text.strip()

                if not content:
                    st.error("Please upload a file or paste document text.")
                else:
                    summary = content[:200] + "..."
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO hr_policies (title, category, version, content, summary, effective_date)
                            VALUES (?, ?, ?, ?, ?, CURRENT_DATE);
                        """, (p_title, p_cat, p_ver, content, summary))
                        cursor.execute("""
                            INSERT INTO audit_logs (user_action, module, performed_by, details)
                            VALUES (?, ?, ?, ?);
                        """, ("POLICY_INGESTED", "Policy Agent", user_role, f"Uploaded policy: {p_title} v{p_ver}"))
                    st.success(f"Policy '{p_title}' ingested and indexed for RAG retrieval!")
                    st.rerun()

