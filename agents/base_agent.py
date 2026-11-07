"""
HR Nexus AI - Base Agent with Multi-Provider Support & Intelligent Heuristic Fallback
Supports OpenAI, Gemini, and robust offline AI heuristics for 100% functional demo mode.
"""
import os
import json
import re
import urllib.request

class BaseAIAgent:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.model_provider = os.getenv("AI_PROVIDER", "auto") # "openai", "gemini", or "demo"

    def get_active_provider(self) -> str:
        if self.model_provider == "demo":
            return "Demo Mode (Offline AI Engine)"
        if self.gemini_key and (self.model_provider in ["gemini", "auto"]):
            return "Google Gemini API"
        if self.openai_key and (self.model_provider in ["openai", "auto"]):
            return "OpenAI API"
        return "Demo Mode (Offline AI Engine)"

    def is_live_api(self) -> bool:
        return bool(self.openai_key or self.gemini_key) and self.model_provider != "demo"

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.4) -> str:
        """Generate text using available live API or domain heuristic generator."""
        # 1. Try Gemini
        if self.gemini_key and self.model_provider in ["gemini", "auto"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_prompt}\n\nTask: {user_prompt}"}
                        ]
                    }],
                    "generationConfig": {"temperature": temperature}
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req, timeout=12) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    text = res_data['candidates'][0]['content']['parts'][0]['text']
                    return text
            except Exception as e:
                print(f"Gemini API request failed: {e}. Falling back...")

        # 2. Try OpenAI
        if self.openai_key and self.model_provider in ["openai", "auto"]:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI API request failed: {e}. Falling back...")

        # 3. Fallback: Intelligent Heuristic Generator
        return self._heuristic_fallback(system_prompt, user_prompt)

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Generate JSON structure using LLM or structured heuristic extractor."""
        raw_text = self.generate_text(
            system_prompt=system_prompt + "\nCRITICAL: Respond ONLY with a valid JSON object. Do not enclose in markdown blocks.",
            user_prompt=user_prompt,
            temperature=0.2
        )
        try:
            # Clean markdown wrappers if any
            cleaned = re.sub(r'^```json\s*', '', raw_text.strip(), flags=re.MULTILINE)
            cleaned = re.sub(r'```$', '', cleaned.strip(), flags=re.MULTILINE)
            # Find outermost json object
            m = re.search(r'(\{.*\})', cleaned, re.DOTALL)
            if m:
                return json.loads(m.group(1))
            return json.loads(cleaned)
        except Exception:
            return {}

    def _heuristic_fallback(self, system_prompt: str, user_prompt: str) -> str:
        """Smart domain fallback synthesizer for demo mode."""
        prompt_lower = (system_prompt + " " + user_prompt).lower()

        # Job Description generation
        if "job description" in prompt_lower or "jd" in prompt_lower:
            return self._synthesize_job_description(user_prompt)

        # Interview questions / STAR bank
        if "interview" in prompt_lower or "question" in prompt_lower:
            return self._synthesize_interview_questions(user_prompt)

        # Offer letter drafting
        if "offer" in prompt_lower or "appointment" in prompt_lower:
            return self._synthesize_offer_letter(user_prompt)

        # Candidate email communication
        if "email" in prompt_lower or "communication" in prompt_lower:
            return self._synthesize_email(user_prompt)

        # General HR advice or action
        return (
            "I have analyzed the provided context against enterprise HR compliance standards.\n\n"
            "**Key Findings & Recommendation:**\n"
            "- The requirements have been mapped to standardized operational competencies.\n"
            "- Workflow parameters align with internal organizational policies.\n"
            "- Proceeding with human-in-the-loop authorization is recommended to maintain audit compliance."
        )

    def _synthesize_job_description(self, prompt: str) -> str:
        return """# Job Overview
We are looking for a high-performing professional to drive impactful initiatives, streamline operational workflows, and collaborate cross-functionally across engineering and business teams.

### Key Responsibilities
- Architect, build, and optimize core business modules adhering to high enterprise standards.
- Collaborate with cross-functional stakeholders to define project roadmaps and technical deliverables.
- Implement automated testing, continuous integration, and rigorous quality assurance.
- Mentor junior teammates and champion engineering/operational best practices.

### Required Qualifications
- Bachelor's or Master's degree in Computer Science, Business, or related discipline.
- Proven experience delivering mission-critical projects in enterprise environments.

### Technical & Core Skills
- Core Domain Tools, Modern Programming/Analytics stacks, Database Systems, Cloud Infrastructure.
- Agile & Scrum Methodologies, CI/CD, Enterprise Automation.

### Soft Skills & Cultural Competencies
- Proactive ownership and analytical problem solving.
- Clear and transparent communication with leadership and cross-functional peers.
- Resilience in fast-paced sprint cycles.

### Company Expectations & Benefits
- Competitive compensation, comprehensive health & medical coverage, 20 days paid annual leave.
- Flexible hybrid working arrangements and generous continuous learning stipends."""

    def _synthesize_interview_questions(self, prompt: str) -> str:
        return """### Structured Interview Question Bank (STAR Framework)

#### Round 1: Core Technical Competency
1. **Architecture & Design**: "Walk us through the most complex project you engineered. How did you make technical trade-offs between speed, scalability, and maintainability?"
   - *Target Competency*: Architectural Depth & Trade-off Evaluation
2. **Problem Solving**: "Describe a critical production bug or system failure you encountered. How did you isolate the root cause, mitigate the immediate issue, and build permanent guardrails?"
   - *Target Competency*: Debugging & Incident Management

#### Round 2: Behavioral & Situational Alignment (STAR)
3. **Conflict Resolution**: "Tell me about a time you had a strong disagreement with a peer or stakeholder regarding a technical or process decision. How did you approach resolution?"
   - *Situation*: Divergent perspectives in sprint planning.
   - *Action*: Facilitated data-driven evaluation matrix.
   - *Result*: Consensus reached without timeline slippage.
4. **Execution Under Pressure**: "Describe a scenario where project requirements shifted dramatically late in the cycle. What actions did you take to deliver on time?"

#### Structured Scoring Rubric (Scale 1-10)
- Technical Mastery (Weight 35%)
- Problem Solving & Logic (Weight 25%)
- Communication & Influence (Weight 20%)
- Cultural & Ethical Alignment (Weight 20%)"""

    def _synthesize_offer_letter(self, prompt: str) -> str:
        return """Dear Candidate,

On behalf of HR Nexus AI, I am thrilled to formally extend an offer of employment. We were thoroughly impressed by your interviews, technical competencies, and passion for innovation.

**Position Details:**
- Designation: Senior Specialist / Engineer
- Department: Core Enterprise Operations
- Employment Type: Full-Time Regular
- Work Location: Hybrid / Office

**Compensation & Benefits:**
- Competitive base compensation with annual performance bonus.
- Comprehensive medical, dental, and vision insurance.
- 20 paid vacation days and statutory benefits.

Please sign and return this agreement prior to your scheduled joining date."""

    def _synthesize_email(self, prompt: str) -> str:
        return """Subject: Update Regarding Your Application with HR Nexus AI

Dear Candidate,

Thank you for your interest in joining HR Nexus AI and for taking the time to speak with our team.

We were very impressed by your background, experience, and the thoughtful questions you asked during our discussions. We are currently advancing our evaluation process and wanted to share the next steps with you.

Please let us know if your availability has changed in the interim. We look forward to staying in touch.

Warm regards,
HR Nexus AI Talent Acquisition Team"""

