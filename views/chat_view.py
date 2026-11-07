"""
HR Nexus AI - View 2: AI HR Agent Conversational Control Center
"""
import streamlit as st
from agents.hr_chat_agent import HRChatAgent
from database.connection import get_db

def render(user_role: str = "HR Manager"):
    st.markdown("### 🤖 AI HR Agent Control Center")
    st.markdown("Interact with the intelligent HR Agent using natural language instructions. The agent parses intent, triggers multi-step workflows, and routes sensitive decisions to human approvals.")

    chat_agent = HRChatAgent()

    # Session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your **HR Nexus AI Agent**. I can help you create job openings, autonomously screen applicant resumes, rank candidates, schedule interviews, draft offer letters, and manage onboarding checklists.\n\nTry clicking any quick action below or type a command in plain English!"
            }
        ]

    # Quick Action Prompt Chips
    st.markdown("##### ⚡ Quick Example Commands")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 'Create a job opening for a Business Analyst'"):
            st.session_state.prompt_input = "Create a job opening for a Business Analyst"
        if st.button("🔍 'Screen all uploaded resumes for Senior Python Developer'"):
            st.session_state.prompt_input = "Screen all uploaded resumes for Senior Python Developer"
    with col2:
        if st.button("🏆 'Find the top 5 candidates for open roles'"):
            st.session_state.prompt_input = "Find the top 5 candidates for open roles"
        if st.button("📅 'Schedule interviews with shortlisted candidates'"):
            st.session_state.prompt_input = "Schedule interviews with shortlisted candidates"
    with col3:
        if st.button("📝 'Generate an offer letter for the selected candidate'"):
            st.session_state.prompt_input = "Generate an offer letter for the selected candidate"
        if st.button("📋 'Show employees whose onboarding documents are pending'"):
            st.session_state.prompt_input = "Show employees whose onboarding documents are pending"

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "action_type" in msg and msg["action_type"] == "REQUIRES_APPROVAL":
                st.info("🛡️ **Action Requires Human-in-the-Loop Sign-off**: Please navigate to the corresponding module to confirm and execute this state change.")

    # Chat Input Box
    default_text = st.session_state.pop("prompt_input", "")
    user_input = st.chat_input("Enter instruction (e.g., 'Screen resumes for Python Developer' or 'Explain leave policy')...")

    prompt_to_run = user_input or default_text

    if prompt_to_run:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        # Process via HR Chat Agent
        with st.spinner("HR Nexus Agent analyzing instruction and coordinating database workflows..."):
            result = chat_agent.process_command(prompt_to_run, user_role=user_role)

        # Append assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "action_type": result.get("action_type"),
            "intent": result.get("intent")
        })
        with st.chat_message("assistant"):
            st.markdown(result["response"])
            if result.get("action_type") == "REQUIRES_APPROVAL":
                st.warning("⚠️ **Human Approval Gate**: This action has been staged and requires authorized HR sign-off before official release.")

        # Log audit trail
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (user_action, module, performed_by, details)
                VALUES (?, ?, ?, ?);
            """, ("NATURAL_LANGUAGE_COMMAND_EXECUTED", "AI Agent", user_role, f"Command: '{prompt_to_run}' -> Intent: {result.get('intent')}"))

