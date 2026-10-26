"""
ChainGuard AI - UI Components and Styling
Provides modern visual styling, custom light theme CSS, KPI metric cards, status badges, and Plotly styling.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Custom CSS for modern Light Theme aesthetics
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
        background-color: #f8fafc;
    }

    /* Modern Card Styles */
    .cg-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .cg-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
        transform: translateY(-2px);
    }

    /* KPI Metric Box */
    .kpi-container {
        display: flex;
        flex-direction: column;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .kpi-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.78rem;
        font-weight: 500;
        margin-top: 6px;
    }
    .delta-pos { color: #16a34a; }
    .delta-neg { color: #dc2626; }
    .delta-neutral { color: #64748b; }

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
        background-color: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fca5a5;
    }
    .badge-high {
        background-color: #fff7ed;
        color: #c2410c;
        border: 1px solid #fdba74;
    }
    .badge-medium {
        background-color: #fefce8;
        color: #a16207;
        border: 1px solid #fde047;
    }
    .badge-low {
        background-color: #f0fdf4;
        color: #15803d;
        border: 1px solid #86efac;
    }

    /* Banner Alert */
    .alert-banner {
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        line-height: 1.45;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }
    .alert-banner-warning {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        color: #92400e;
        border-top: 1px solid #fef3c7;
        border-right: 1px solid #fef3c7;
        border-bottom: 1px solid #fef3c7;
    }
    .alert-banner-critical {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        color: #991b1b;
        border-top: 1px solid #fee2e2;
        border-right: 1px solid #fee2e2;
        border-bottom: 1px solid #fee2e2;
    }
    .alert-banner-info {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        color: #1e40af;
        border-top: 1px solid #dbeafe;
        border-right: 1px solid #dbeafe;
        border-bottom: 1px solid #dbeafe;
    }
    .alert-banner-success {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        color: #166534;
        border-top: 1px solid #dcfce7;
        border-right: 1px solid #dcfce7;
        border-bottom: 1px solid #dcfce7;
    }

    /* Brand Header */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1e40af 0%, #4338ca 50%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2px;
    }
    .brand-sub {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 16px;
    }

    /* Sidebar Clean Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
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
        <hr style="border: 0; height: 1px; background: linear-gradient(90deg, #2563eb 0%, #cbd5e1 100%); margin-top: 6px; margin-bottom: 18px;" />
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(title, value, delta=None, delta_text="", is_positive=True, border_color="#2563eb"):
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
    """Returns clean, modern light theme layout parameters for Plotly figures."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter, sans-serif", color="#1e293b", size=12),
        margin=dict(l=40, r=30, t=40, b=40),
        xaxis=dict(
            gridcolor="#f1f5f9",
            linecolor="#cbd5e1",
            tickfont=dict(color="#64748b"),
            title=dict(font=dict(color="#334155"))
        ),
        yaxis=dict(
            gridcolor="#f1f5f9",
            linecolor="#cbd5e1",
            tickfont=dict(color="#64748b"),
            title=dict(font=dict(color="#334155"))
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(color="#1e293b")
        )
    )
