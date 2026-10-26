"""
ChainGuard AI - Page 11: Financial Impact Analysis
Quantifies and audits the financial exposure of supply chain disruptions:
Production idle losses, expedited air logistics, customer SLA penalties,
excess inventory holding costs, and emergency spot sourcing premiums.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_components import (
    apply_custom_styles, render_header, render_alert,
    get_plotly_theme
)
from modules.inventory_analysis import calculate_inventory_metrics
from modules.production_risk import evaluate_production_material_risk
from modules.financial_analysis import compute_financial_impact_breakdown

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Financial Disruption & Operations Cost Impact",
        subtitle="Financial quantification of supply chain disruption exposure across manufacturing, procurement, and logistics"
    )

    inv_df = data_dict.get("inventory", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())
    prod_df = data_dict.get("production", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())
    trans_df = data_dict.get("transportation", pd.DataFrame())

    if inv_df.empty:
        st.warning("Insufficient data available for financial modeling.")
        return

    # User-Configurable Financial Assumptions
    with st.expander("⚙️ Corporate Financial & Cost Model Assumptions", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            annual_holding = st.slider("Annual Inventory Carrying Cost Rate (%):", 10.0, 35.0, 22.0, 1.0) / 100.0
        with c2:
            idle_day_cost = st.number_input("Plant Production Line Idle Cost ($/day):", value=1200.0, step=100.0)
        with c3:
            sla_penalty_pct = st.slider("Customer Late Delivery SLA Penalty Rate (%):", 0.5, 5.0, 2.0, 0.5) / 100.0

    # Compute dependencies and financial breakdown
    inv_metrics = calculate_inventory_metrics(inv_df, pos_df)
    prod_eval, _ = evaluate_production_material_risk(prod_df, bom_df, inv_metrics, pos_df)
    df_cost, fin_summary = compute_financial_impact_breakdown(
        inv_metrics,
        prod_eval,
        pos_df,
        trans_df,
        annual_holding_rate=annual_holding,
        idle_cost_per_day=idle_day_cost,
        late_penalty_rate=sla_penalty_pct
    )

    tot_exposure = fin_summary.get("total_financial_exposure", 0)

    # 1. Executive Summary Banner
    render_alert(
        f"<strong>TOTAL AGGREGATE FINANCIAL EXPOSURE: ${tot_exposure:,.2f}</strong><br/>"
        f"Manufacturing idle-line risk represents the largest exposure component at "
        f"<strong>${fin_summary.get('idle_capacity_losses', 0):,.2f}</strong>, followed by "
        f"<strong>${fin_summary.get('expedited_freight_spend', 0):,.2f}</strong> in premium air freight expediting and "
        f"<strong>${fin_summary.get('sla_delay_penalties', 0):,.2f}</strong> in contractual SLA delay penalties.",
        alert_type="critical" if tot_exposure > 50000 else "warning",
        title="Audited Disruption Cost Exposure"
    )

    # 2. Executive KPI Summary Cards
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        st.metric("Total Disruption Exposure", f"${tot_exposure:,.0f}", delta="Cumulative Risk")
    with f2:
        st.metric("Idle Line Losses", f"${fin_summary.get('idle_capacity_losses', 0):,.0f}", delta="Manufacturing Plants", delta_color="inverse")
    with f3:
        st.metric("Expedited Air Freight", f"${fin_summary.get('expedited_freight_spend', 0):,.0f}", delta="Logistics Premium")
    with f4:
        st.metric("Customer SLA Penalties", f"${fin_summary.get('sla_delay_penalties', 0):,.0f}", delta="Commercial Contracts", delta_color="inverse")
    with f5:
        st.metric("Excess Inventory Holding", f"${fin_summary.get('excess_holding_cost', 0):,.0f}", delta="Working Capital Drag")

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 20px 0;' />", unsafe_allow_html=True)

    # 3. Financial Breakdown Table Distinguishing Data Sources
    st.markdown("### 📋 Audited Cost Exposure Breakdown")
    st.write("Separating actual recorded expenses, calculated metrics, and model-based statistical estimates to prevent double counting:")

    st.dataframe(
        df_cost,
        column_config={
            "Amount ($)": st.column_config.NumberColumn("Exposure Amount", format="$%.2f")
        },
        use_container_width=True
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visual Diagnostics: Cost Exposure Waterfall & Departmental Allocation
    c_v1, c_v2 = st.columns(2)

    with c_v1:
        st.markdown("#### Cumulative Financial Exposure Waterfall ($)")
        wf_cats = df_cost["Cost Category"].tolist() + ["Total Disruption Exposure"]
        wf_vals = df_cost["Amount ($)"].tolist() + [tot_exposure]
        wf_measures = ["relative"] * len(df_cost) + ["total"]

        fig_wf = go.Figure(go.Waterfall(
            name="Disruption Costs",
            orientation="v",
            measure=wf_measures,
            x=[c[:22] + "..." for c in wf_cats],
            textposition="outside",
            text=[f"${v:,.0f}" for v in wf_vals],
            y=df_cost["Amount ($)"].tolist() + [0],
            connector={"line": {"color": "#4b5563"}},
            decreasing={"marker": {"color": "#10b981"}},
            increasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#8b5cf6"}}
        ))
        fig_wf.update_layout(**get_plotly_theme(), height=360)
        st.plotly_chart(fig_wf, use_container_width=True)

    with c_v2:
        st.markdown("#### Disruption Exposure by Department")
        fig_dept = px.pie(
            df_cost,
            values="Amount ($)",
            names="Impacted Area",
            hole=0.45,
            color_discrete_sequence=["#ef4444", "#3b82f6", "#f59e0b", "#10b981", "#8b5cf6"]
        )
        fig_dept.update_layout(**get_plotly_theme(), height=360)
        st.plotly_chart(fig_dept, use_container_width=True)

    # Governance Notice
    st.markdown("""
    <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #475569; border: 1px solid #e2e8f0; margin-top: 20px;">
        <strong>Methodological Clarity:</strong> Financial figures strictly segregate recorded procurement outlays from model-based idle-time estimates 
        to avoid double-counting across the cost-of-goods-sold (COGS) and operational expense (OpEx) accounts.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
