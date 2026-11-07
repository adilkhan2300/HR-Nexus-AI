"""
HR Nexus AI - Professional Enterprise SaaS Styling & UI Theme
"""

MAIN_CSS = """
<style>
/* Main typography and reset */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header & Brand Container */
.nexus-brand-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
    padding: 1.5rem 2rem;
    border-radius: 14px;
    color: #ffffff;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

.nexus-brand-title {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
}

.nexus-brand-subtitle {
    font-size: 0.95rem;
    color: #94a3b8;
    font-weight: 400;
}

/* Metric / KPI Card */
.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 1rem;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.08);
}
.metric-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 0.35rem;
}
.metric-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.2;
}
.metric-delta {
    font-size: 0.8rem;
    font-weight: 500;
    color: #10b981;
    margin-top: 0.25rem;
}

/* Badge Pills */
.nexus-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    line-height: 1;
}
.badge-blue { background-color: #dbeafe; color: #1e40af; }
.badge-green { background-color: #d1fae5; color: #065f46; }
.badge-amber { background-color: #fef3c7; color: #92400e; }
.badge-red { background-color: #fee2e2; color: #991b1b; }
.badge-purple { background-color: #ede9fe; color: #5b21b6; }
.badge-slate { background-color: #f1f5f9; color: #475569; }

/* Workflow Step Box */
.workflow-step {
    border-left: 3px solid #2563eb;
    padding-left: 1rem;
    margin-bottom: 1rem;
    background: #f8fafc;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
}
.workflow-step-title {
    font-weight: 700;
    color: #1e293b;
    font-size: 0.95rem;
}
.workflow-step-desc {
    font-size: 0.85rem;
    color: #64748b;
}

/* Chat bubble styling */
.chat-bubble-user {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px 12px 2px 12px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.75rem;
    color: #1e3a8a;
}
.chat-bubble-agent {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px 12px 12px 2px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}

/* Kanban column */
.kanban-column {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.75rem;
    min-height: 380px;
}
.kanban-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #334155;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
}
.kanban-card {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kanban-card b, .kanban-card strong, .kanban-card .cand-name {
    color: #0f172a !important;
    font-weight: 700;
}
</style>
"""

