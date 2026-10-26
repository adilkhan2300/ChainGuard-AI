"""
ChainGuard AI - Page 9: Strategy Cost Comparison
Decision-support module comparing 5 response options for material shortages:
Expedite PO, Alternative Supplier, Inter-Plant Transfer, Approved Substitute, Reschedule.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_components import (
    apply_custom_styles, render_header, render_alert,
    get_plotly_theme, get_badge
)
from modules.strategy_cost_comparison import evaluate_mitigation_strategies

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Mitigation Strategy & Trade-off Cost Comparison",
        subtitle="Multi-criteria decision support comparing operational feasibility, lead times, and cost trade-offs"
    )

    inv_df = data_dict.get("inventory", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())

    if inv_df.empty:
        st.warning("Insufficient data available to run strategy comparison.")
        return

    # Shortage Material Selection
    crit_materials = inv_df[inv_df["current_stock"] < inv_df["reorder_point"]]["material_id"].unique().tolist()
    if not crit_materials:
        crit_materials = inv_df["material_id"].unique().tolist()[:10]

    st.markdown("### 🎯 Configure Shortage Scenario for Evaluation")
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_mat = st.selectbox("Target Shortage Material SKU:", crit_materials)
        mat_info = inv_df[inv_df["material_id"] == selected_mat].iloc[0]
        st.caption(f"**Description:** {mat_info['material_name']} | **Unit Cost:** ${mat_info['inventory_unit_cost']:.2f}")
    with c2:
        shortage_units = st.number_input("Shortage Quantity (units)", value=300, min_value=50, step=50)
    with c3:
        target_days = st.number_input("Target Required In-Plant Window (Days)", value=7, min_value=1, step=1)

    # Check BOM for approved substitute
    has_sub = False
    if not bom_df.empty:
        sub_records = bom_df[bom_df["material_id"] == selected_mat]
        if not sub_records.empty:
            alt_val = sub_records.iloc[0].get("approved_alternative_material", "None")
            has_sub = (alt_val != "None" and pd.notna(alt_val))

    # Evaluate strategies
    df_strat = evaluate_mitigation_strategies(
        material_id=selected_mat,
        shortage_qty=shortage_units,
        target_date_days=target_days,
        unit_cost=float(mat_info["inventory_unit_cost"]),
        has_alternative=has_sub
    )

    # 1. Preferred Strategy Banner
    recommended_row = df_strat[df_strat["is_recommended"]].iloc[0]
    render_alert(
        f"<strong>OPTIMAL MITIGATION STRATEGY RECOMMENDED:</strong> <strong>{recommended_row['strategy_name']}</strong><br/>"
        f"Estimated Total Cost: <strong>${recommended_row['total_estimated_cost']:,.2f}</strong> | "
        f"Time to Availability: <strong>{recommended_row['lead_time_days']} Days</strong> (Feasibility: {recommended_row['feasibility']}) | "
        f"Residual Shortage: <strong>{recommended_row['residual_shortage']} units</strong>.<br/>"
        f"<strong>Trade-off Rationale:</strong> {recommended_row['tradeoff_verdict']}",
        alert_type="success",
        title="Algorithmic Decision Optimization Verdict"
    )

    # 2. Strategy Trade-Off Comparison Matrix
    st.markdown("### ⚖️ Multi-Criteria Strategy Decision Matrix")

    display_cols = [
        "strategy_id", "strategy_name", "total_estimated_cost",
        "lead_time_days", "quantity_recovered", "residual_shortage",
        "feasibility", "risk_reduction_score", "operational_dependencies"
    ]
    st.dataframe(
        df_strat[display_cols],
        column_config={
            "total_estimated_cost": st.column_config.NumberColumn("Total Cost ($)", format="$%.2f"),
            "lead_time_days": st.column_config.NumberColumn("Lead Time (Days)", format="%d d"),
            "quantity_recovered": st.column_config.NumberColumn("Recovered Qty", format="%d"),
            "residual_shortage": st.column_config.NumberColumn("Residual Gap", format="%d"),
            "risk_reduction_score": st.column_config.ProgressColumn("Resilience Score", min_value=0, max_value=100, format="%d")
        },
        use_container_width=True
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 3. Visual Diagnostics: Cost vs Lead Time Tradeoff Plot
    c_v1, c_v2 = st.columns(2)

    with c_v1:
        st.markdown("#### Cost vs Time-to-Availability Trade-off")
        fig_trade = px.scatter(
            df_strat,
            x="lead_time_days",
            y="total_estimated_cost",
            size="risk_reduction_score",
            color="feasibility",
            text="strategy_id",
            hover_name="strategy_name",
            color_discrete_map={
                "High": "#10b981",
                "Moderate": "#f59e0b",
                "Low": "#ef4444",
                "Unfeasible (No Approved Alternative)": "#6b7280"
            },
            labels={
                "lead_time_days": "Lead Time to Availability (Days)",
                "total_estimated_cost": "Total Estimated Strategy Cost ($)"
            }
        )
        fig_trade.add_vline(x=target_days, line_dash="dash", line_color="#ef4444", annotation_text=f"Cutoff ({target_days}d)")
        fig_trade.update_traces(textposition="top center")
        fig_trade.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_trade, use_container_width=True)

    with c_v2:
        st.markdown("#### Residual Shortage Volume by Option")
        fig_res = px.bar(
            df_strat,
            x="strategy_id",
            y="residual_shortage",
            color="feasibility",
            hover_name="strategy_name",
            text_auto=True,
            color_discrete_map={
                "High": "#10b981",
                "Moderate": "#f59e0b",
                "Low": "#ef4444",
                "Unfeasible (No Approved Alternative)": "#6b7280"
            },
            labels={"residual_shortage": "Unresolved Shortage (Units)", "strategy_id": "Strategy Option"}
        )
        fig_res.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_res, use_container_width=True)

    # 4. Strategy Deep-Dive Cards
    st.markdown("### 📝 Detailed Strategy Operational Specifications")
    for _, strat in df_strat.iterrows():
        with st.expander(f"🔹 [{strat['strategy_id']}] {strat['strategy_name']} — Total: ${strat['total_estimated_cost']:,.2f}"):
            st.markdown(f"**Description:** {strat['description']}")
            s1, s2 = st.columns(2)
            with s1:
                st.markdown(f"**Lead Time:** `{strat['lead_time_days']} Days` | **Feasibility:** `{strat['feasibility']}`")
                st.markdown(f"**Recovered Quantity:** `{strat['quantity_recovered']} Units` | **Residual Gap:** `{strat['residual_shortage']} Units`")
            with s2:
                st.markdown(f"**Operational Prerequisite:** {strat['operational_dependencies']}")
                st.markdown(f"**Cost Breakdown:** `{strat['cost_breakdown']}`")

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
