"""
ChainGuard AI - UI Components and Styling
Provides modern visual styling, custom CSS, KPI metric cards, status badges, and Plotly styling.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Custom CSS for rich aesthetics
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }

    /* Modern Card Styles */
    .cg-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .cg-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }

    /* KPI Metric Box */
    .kpi-container {
        display: flex;
        flex-direction: column;
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px;
        position: relative;
        overflow: hidden;
    }
    .kpi-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9ca3af;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f9fafb;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .delta-pos { color: #10b981; }
    .delta-neg { color: #ef4444; }
    .delta-neutral { color: #6b7280; }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-high {
        background-color: rgba(249, 115, 22, 0.2);
        color: #fb923c;
        border: 1px solid rgba(249, 115, 22, 0.4);
    }
    .badge-medium {
        background-color: rgba(234, 179, 8, 0.2);
        color: #facc15;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }
    .badge-low {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    /* Banner Alert */
    .alert-banner {
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .alert-banner-warning {
        background: rgba(245, 158, 11, 0.12);
        border-left: 4px solid #f59e0b;
        color: #fef3c7;
    }
    .alert-banner-critical {
        background: rgba(239, 68, 68, 0.12);
        border-left: 4px solid #ef4444;
        color: #fee2e2;
    }
    .alert-banner-info {
        background: rgba(59, 130, 246, 0.12);
        border-left: 4px solid #3b82f6;
        color: #dbeafe;
    }
    .alert-banner-success {
        background: rgba(16, 185, 129, 0.12);
        border-left: 4px solid #10b981;
        color: #d1fae5;
    }

    /* Brand Header */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .brand-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 16px;
    }

    /* Sidebar Clean Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1f2937;
    }
</style>
"""

def apply_custom_styles():
    """Injects high-end styling into the Streamlit session."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_header(title="ChainGuard AI", subtitle="Supply Chain Risk Prediction & Resilience Intelligence Platform"):
    """Renders the executive brand banner."""
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div class="brand-title">{title}</div>
        <div class="brand-sub">{subtitle}</div>
        <hr style="border: 0; height: 1px; background: linear-gradient(90deg, #3b82f6 0%, transparent 100%); margin-top: 6px; margin-bottom: 18px;" />
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(title, value, delta=None, delta_text="", is_positive=True, border_color="#3b82f6"):
    """Renders a sleek KPI metric card."""
    delta_class = "delta-pos" if is_positive else "delta-neg"
    delta_symbol = "▲" if is_positive else "▼"
    delta_html = f'<div class="kpi-delta {delta_class}">{delta_symbol} {delta_text}</div>' if delta_text else ''
    
    html = f"""
    <div class="kpi-container" style="border-top: 3px solid {border_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    return html

def get_badge(text, level="low"):
    """Returns HTML for a risk badge (critical, high, medium, low)."""
    lvl = level.lower()
    if "crit" in lvl:
        cls = "badge-critical"
    elif "high" in lvl:
        cls = "badge-high"
    elif "med" in lvl:
        cls = "badge-medium"
    else:
        cls = "badge-low"
    return f'<span class="badge {cls}">{text}</span>'

def render_alert(text, alert_type="warning", title=None):
    """Renders an alert box (critical, warning, info, success)."""
    type_map = {
        "critical": "alert-banner-critical",
        "warning": "alert-banner-warning",
        "info": "alert-banner-info",
        "success": "alert-banner-success"
    }
    cls = type_map.get(alert_type, "alert-banner-info")
    title_html = f"<strong>{title}</strong><br/>" if title else ""
    st.markdown(f'<div class="alert-banner {cls}">{title_html}{text}</div>', unsafe_allow_html=True)

def get_plotly_theme():
    """Returns standard sleek dark theme layout parameters for Plotly figures."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.7)",
        font=dict(family="Inter, sans-serif", color="#e5e7eb", size=12),
        margin=dict(l=40, r=30, t=40, b=40),
        xaxis=dict(
            gridcolor="#1f2937",
            linecolor="#374151",
            tickfont=dict(color="#9ca3af"),
            title_font=dict(color="#d1d5db")
        ),
        yaxis=dict(
            gridcolor="#1f2937",
            linecolor="#374151",
            tickfont=dict(color="#9ca3af"),
            title_font=dict(color="#d1d5db")
        ),
        legend=dict(
            bgcolor="rgba(17,24,39,0.8)",
            bordercolor="#374151",
            borderwidth=1,
            font=dict(color="#e5e7eb")
        )
    )
