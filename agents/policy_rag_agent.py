"""
HR Nexus AI - HR Policy and SOP Knowledge Agent
Provides RAG (Retrieval-Augmented Generation) question answering across corporate HR policies,
employee handbooks, and standard operating procedures with source document and section citations.
"""
import re
from agents.base_agent import BaseAIAgent
from database.connection import get_db

class PolicyRAGAgent(BaseAIAgent):
    def answer_query(self, query: str) -> dict:
        """Search policy repository and answer query with verifiable citations."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, version, content, summary FROM hr_policies;")
            policies = [dict(r) for r in cursor.fetchall()]

        if not policies:
            return {
                "answer": "No HR policies or SOP documents are currently loaded in the repository.",
                "citations": []
            }

        query_terms = [t.lower() for t in re.findall(r'\b\w{3,}\b', query)]

        scored_chunks = []
        for pol in policies:
            sections = pol['content'].split('\n\n')
            for sec in sections:
                sec_text = sec.strip()
                if not sec_text:
                    continue
                score = sum(1 for term in query_terms if term in sec_text.lower())
                if score > 0:
                    scored_chunks.append({
                        "policy_title": pol['title'],
                        "category": pol['category'],
                        "version": pol['version'],
                        "section_text": sec_text,
                        "score": score
                    })

        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        top_chunks = scored_chunks[:3]

        if not top_chunks:
            return {
                "answer": (
                    f"I could not locate specific guidelines regarding '{query}' in our uploaded HR policies and SOPs. "
                    "In adherence with company compliance, I do not extrapolate or invent company policy. "
                    "Please contact Human Resources or the People Operations committee directly for guidance."
                ),
                "citations": []
            }

        # Build context for LLM synthesis or structured fallback
        context_str = "\n\n".join([
            f"[Source: {c['policy_title']} (v{c['version']})]\n{c['section_text']}"
            for c in top_chunks
        ])

        system_prompt = (
            "You are an authoritative Corporate HR Compliance Assistant. "
            "Answer the employee query strictly using the provided policy excerpts. "
            "Always state the source policy title and section. If the answer is not in the context, explicitly say so."
        )
        user_prompt = f"Policy Excerpts:\n{context_str}\n\nEmployee Query: {query}\n\nProvide a clear, helpful, factual answer citing the policy."

        # If live API available, synthesize answer; else generate clean structured answer from top chunk
        if self.is_live_api():
            answer_text = self.generate_text(system_prompt, user_prompt, temperature=0.2)
        else:
            primary = top_chunks[0]
            answer_text = (
                f"According to the **{primary['policy_title']} (v{primary['version']})**:\n\n"
                f"{primary['section_text']}\n\n"
                f"*Policy Reference: HR Nexus Internal Operations / {primary['category']}*"
            )

        citations = [
            {"policy": c['policy_title'], "category": c['category'], "snippet": c['section_text'][:160] + "..."}
            for c in top_chunks
        ]

        return {
            "query": query,
            "answer": answer_text,
            "citations": citations
        }

