"""
HR Nexus AI - UI Helper Functions and Visual Components
"""
import streamlit as st
from config import STAGE_COLORS

def render_brand_header(role_name: str = "HR Manager", active_provider: str = "Demo Mode"):
    provider_badge_class = "badge-green" if "API" in active_provider else "badge-purple"
    st.markdown(f"""
    <div class="nexus-brand-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <div class="nexus-brand-title">
                    <span>⚡ HR Nexus AI</span>
                    <span class="nexus-badge badge-blue">Enterprise v2.0</span>
                </div>
                <div class="nexus-brand-subtitle">
                    Autonomous Recruitment & Onboarding Agent • Human-in-the-Loop Governance
                </div>
            </div>
            <div style="margin-top: 0.5rem; text-align: right;">
                <span class="nexus-badge {provider_badge_class}">Engine: {active_provider}</span>
                <span class="nexus-badge badge-amber" style="margin-left: 6px;">Role: {role_name}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label: str, value: str, delta: str = None, color: str = "#2563eb"):
    delta_html = f'<div class="metric-delta" style="color: {color};">{delta}</div>' if delta else ''
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def render_badge(text: str, badge_type: str = "blue"):
    return f'<span class="nexus-badge badge-{badge_type}">{text}</span>'

def render_stage_pill(stage: str):
    color = STAGE_COLORS.get(stage, "#64748b")
    return f'<span style="background-color: {color}20; color: {color}; border: 1px solid {color}40; border-radius: 9999px; padding: 2px 8px; font-size: 0.75rem; font-weight: 600;">{stage}</span>'

