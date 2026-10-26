"""
ChainGuard AI - Page 3: Supplier Risk Intelligence
Evaluates supplier delivery delays, lead-time variability, order fulfillment,
single-source dependencies, and multi-factor risk scores.
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
from modules.supplier_risk import calculate_supplier_metrics, calculate_composite_supplier_score

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Supplier Risk & Reliability Intelligence",
        subtitle="Empirical tracking of vendor lead times, fulfillment rates, financial solvency, and single-source exposure"
    )

    sups_df = data_dict.get("suppliers", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())

    if sups_df.empty or pos_df.empty:
        st.warning("Insufficient supplier or purchase order data available for evaluation.")
        return

    # Compute metrics
    sup_metrics = calculate_supplier_metrics(sups_df, pos_df, bom_df)

    # 1. Weight Configuration Expander
    with st.expander("⚙️ Configure Multi-Factor Risk Score Weights", expanded=False):
        st.write("Adjust the weighting formula applied to normalize empirical supplier metrics into a 0-100 composite index:")
        wc1, wc2, wc3, wc4, wc5, wc6 = st.columns(6)
        with wc1:
            w_otd = st.slider("OTD Unreliability", 0.0, 0.5, 0.25, 0.05)
        with wc2:
            w_lt = st.slider("Lead-Time Variance", 0.0, 0.5, 0.20, 0.05)
        with wc3:
            w_ful = st.slider("Fulfillment Shortfall", 0.0, 0.5, 0.15, 0.05)
        with wc4:
            w_qual = st.slider("Quality Defect Rate", 0.0, 0.5, 0.15, 0.05)
        with wc5:
            w_fin = st.slider("Financial Risk", 0.0, 0.5, 0.15, 0.05)
        with wc6:
            w_ss = st.slider("Single-Source Dependency", 0.0, 0.5, 0.10, 0.05)

        total_w = w_otd + w_lt + w_ful + w_qual + w_fin + w_ss
        if abs(total_w - 1.0) > 0.01:
            st.caption(f"⚠️ Note: Weights sum to {total_w:.2f}. System automatically normalizes to 1.0.")
            w_otd /= total_w
            w_lt /= total_w
            w_ful /= total_w
            w_qual /= total_w
            w_fin /= total_w
            w_ss /= total_w

        custom_weights = {
            "otd": w_otd, "lt_variability": w_lt, "fulfillment": w_ful,
            "quality": w_qual, "financial": w_fin, "single_source": w_ss
        }
        sup_metrics = calculate_composite_supplier_score(sup_metrics, custom_weights)

    # 2. Executive Supplier Metrics Summary
    top_critical = sup_metrics[sup_metrics["risk_level"].isin(["Critical", "Elevated Risk"])]
    render_alert(
        f"<strong>SUPPLIER DISRUPTION VULNERABILITY:</strong> Identified <strong>{len(top_critical)} suppliers</strong> "
        f"with elevated or critical risk profiles. Average vendor lead-time variance across the network is "
        f"<strong>{sup_metrics['lead_time_std_dev'].mean():.1f} days</strong>. Single-source supplier dependencies affect "
        f"<strong>{sup_metrics['single_source_materials'].sum()} critical materials</strong>.",
        alert_type="warning" if len(top_critical) > 0 else "info"
    )

    # 3. Interactive Supplier Ranking Table
    st.markdown("### 🏆 Comprehensive Supplier Risk Rankings")

    search_term = st.text_input("🔍 Search by Supplier Name, Location, or Material Category:", "")
    filtered_sups = sup_metrics.copy()
    if search_term:
        mask = (
            filtered_sups["supplier_name"].str.contains(search_term, case=False, na=False) |
            filtered_sups["supplier_location"].str.contains(search_term, case=False, na=False) |
            filtered_sups["material_categories"].str.contains(search_term, case=False, na=False)
        )
        filtered_sups = filtered_sups[mask]

    display_cols = [
        "supplier_id", "supplier_name", "supplier_location",
        "contractual_lead_time_days", "avg_actual_lead_time", "lead_time_std_dev",
        "on_time_delivery_rate", "fulfillment_rate", "quality_rating",
        "financial_risk_score", "supplier_risk_score", "risk_level"
    ]
    st.dataframe(
        filtered_sups[display_cols].sort_values("supplier_risk_score", ascending=False),
        column_config={
            "on_time_delivery_rate": st.column_config.ProgressColumn("OTD Rate", format="%.1f", min_value=0, max_value=1),
            "supplier_risk_score": st.column_config.NumberColumn("Risk Score (0-100)", format="%.1f"),
            "financial_risk_score": st.column_config.NumberColumn("Financial Solvency Risk", format="%.2f")
        },
        use_container_width=True,
        height=320
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visualizations: Lead Time Slippage & Geographic Concentration
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("#### Contractual vs Actual Lead Time (Days)")
        chart_df = sup_metrics.sort_values("supplier_risk_score", ascending=False).head(10)
        fig_lt = go.Figure()
        fig_lt.add_trace(go.Bar(
            x=chart_df["supplier_name"].str.slice(0, 18),
            y=chart_df["contractual_lead_time_days"],
            name="Contractual Lead Time",
            marker_color="#3b82f6"
        ))
        fig_lt.add_trace(go.Bar(
            x=chart_df["supplier_name"].str.slice(0, 18),
            y=chart_df["avg_actual_lead_time"],
            name="Actual Avg Lead Time",
            marker_color="#ef4444"
        ))
        fig_lt.update_layout(
            barmode="group",
            **get_plotly_theme(),
            height=340,
            xaxis_tickangle=-35
        )
        st.plotly_chart(fig_lt, use_container_width=True)

    with col_v2:
        st.markdown("#### Geographic Distribution of Sourcing Risk")
        loc_df = sup_metrics.groupby("supplier_location").agg({
            "supplier_risk_score": "mean",
            "supplier_id": "count"
        }).reset_index().rename(columns={"supplier_id": "Supplier Count"})
        fig_loc = px.bar(
            loc_df.sort_values("supplier_risk_score", ascending=False).head(8),
            x="supplier_risk_score",
            y="supplier_location",
            orientation="h",
            color="supplier_risk_score",
            color_continuous_scale="Reds",
            labels={"supplier_risk_score": "Avg Risk Score", "supplier_location": "Sourcing Hub"}
        )
        fig_loc.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_loc, use_container_width=True)

    # 5. Deep-Dive Supplier Drilldown
    st.markdown("### 🔍 Supplier Deep-Dive Investigation")
    selected_sup_id = st.selectbox(
        "Select Supplier for Operational Audit:",
        options=sup_metrics["supplier_id"].tolist(),
        format_func=lambda x: f"{x} - {sup_metrics[sup_metrics['supplier_id'] == x]['supplier_name'].values[0]}"
    )

    if selected_sup_id:
        s_data = sup_metrics[sup_metrics["supplier_id"] == selected_sup_id].iloc[0]
        s_pos = pos_df[pos_df["supplier_id"] == selected_sup_id].copy()

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.metric("Vendor Risk Score", f"{s_data['supplier_risk_score']:.1f} / 100", delta=s_data["risk_level"])
        with d2:
            st.metric("On-Time Delivery Rate", f"{s_data['on_time_delivery_rate']*100:.1f}%", delta=f"{s_data['delayed_pos']} late orders")
        with d3:
            st.metric("Avg Delivery Delay", f"{s_data['avg_delay_days']:.1f} days", delta=f"Std Dev: {s_data['lead_time_std_dev']:.1f}d")
        with d4:
            st.metric("Single-Source Materials", f"{s_data['single_source_materials']} Critical SKUs", delta="High Dependency" if s_data['is_single_source'] else "Diversified")

        st.markdown(f"**Associated Purchase Orders for {s_data['supplier_name']} ({len(s_pos)} orders):**")
        st.dataframe(s_pos.head(10), use_container_width=True)

    # Governance Notice
    st.markdown("""
    <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #475569; border: 1px solid #e2e8f0; margin-top: 20px;">
        <strong>Methodological Clarity:</strong> The Supplier Risk Score is a relative operational ranking index derived from 
        empirical delivery receipts, quality ratings, and financial scorecards. It does NOT represent an actuarial or default failure probability.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
