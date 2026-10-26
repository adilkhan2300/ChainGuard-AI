"""
ChainGuard AI - Page 5: Production Disruption Analysis
BOM Explosion, material readiness checks, manufacturing delay windows,
and plant-level line starvation risk evaluation.
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
from modules.production_risk import evaluate_production_material_risk
from modules.inventory_analysis import calculate_inventory_metrics

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Production Disruption & BOM Risk Analysis",
        subtitle="Cross-reference planned manufacturing orders against BOM component availability and supplier deliveries"
    )

    prod_df = data_dict.get("production", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())
    inv_df = data_dict.get("inventory", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())

    if prod_df.empty or bom_df.empty or inv_df.empty:
        st.warning("Insufficient data. Requires production.csv, bill_of_materials.csv, and inventory.csv.")
        return

    # Compute inventory and production risk
    inv_metrics = calculate_inventory_metrics(inv_df, pos_df)
    eval_prod_df, summary = evaluate_production_material_risk(prod_df, bom_df, inv_metrics, pos_df)

    # 1. Summary Highlights Banner
    crit_orders = summary.get("critical_orders", 0)
    orders_at_risk = summary.get("orders_at_risk", 0)
    tot_impact = summary.get("total_impact_cost", 0)

    render_alert(
        f"<strong>MANUFACTURING DISRUPTION RISK:</strong> <strong>{crit_orders} Production Orders</strong> are facing imminent line starvation "
        f"due to missing critical BOM components. Total estimated idle capacity & delay exposure: <strong>${tot_impact:,.2f}</strong>. "
        f"Recommended priority: Resequence master assembly lines to avoid unutilized line downtime.",
        alert_type="critical" if crit_orders > 0 else "info"
    )

    # 2. Executive KPI Summary Cards
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.metric("Total Production Orders", f"{summary.get('total_production_orders', 0)} Orders", delta="Across 3 Plants")
    with p2:
        st.metric("Orders with Material Shortage", f"{orders_at_risk} Orders", delta="Requires Mitigation", delta_color="inverse")
    with p3:
        avg_delay = round(eval_prod_df["potential_delay_days"].mean(), 1)
        st.metric("Average Delay Window", f"{avg_delay} Days", delta="Past Scheduled Start", delta_color="inverse")
    with p4:
        st.metric("Idle Capacity Cost Exposure", f"${tot_impact:,.2f}", delta="Estimated Downtime Penalty", delta_color="inverse")

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 20px 0;' />", unsafe_allow_html=True)

    # 3. Production Orders Risk Master Table
    st.markdown("### 🏭 Production Order Readiness & Schedule Risk")

    plant_filter = st.multiselect(
        "Filter by Manufacturing Plant:",
        options=sorted(eval_prod_df["plant_id"].unique().tolist()),
        default=sorted(eval_prod_df["plant_id"].unique().tolist())
    )

    filtered_df = eval_prod_df[eval_prod_df["plant_id"].isin(plant_filter)] if plant_filter else eval_prod_df

    display_cols = [
        "production_order_id", "product_id", "plant_id", "planned_start_date",
        "planned_quantity", "risk_level", "potential_delay_days",
        "expected_replenishment_date", "estimated_production_impact_cost", "suggested_mitigation"
    ]

    st.dataframe(
        filtered_df[display_cols].sort_values("potential_delay_days", ascending=False),
        column_config={
            "planned_quantity": st.column_config.NumberColumn("Batch Qty", format="%d"),
            "potential_delay_days": st.column_config.NumberColumn("Delay (Days)", format="%d"),
            "estimated_production_impact_cost": st.column_config.NumberColumn("Idle Cost ($)", format="$%.2f")
        },
        use_container_width=True,
        height=320
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visual Diagnostics: Delay Windows & Component Shortage Pareto
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Production Orders Potential Delay Window (Days)")
        chart_prods = filtered_df.sort_values("potential_delay_days", ascending=False).head(10)
        fig_delay = px.bar(
            chart_prods,
            x="production_order_id",
            y="potential_delay_days",
            color="risk_level",
            hover_name="product_id",
            color_discrete_map={
                "Critical Shortage - Delay Imminent": "#ef4444",
                "Moderate Material Risk": "#f97316",
                "Ready / Low Risk": "#10b981"
            },
            labels={"potential_delay_days": "Potential Delay (Days)", "production_order_id": "Production Order"}
        )
        fig_delay.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_delay, use_container_width=True)

    with c2:
        st.markdown("#### Idle Line Impact Cost Exposure by Plant ($)")
        plant_cost = filtered_df.groupby("plant_id")["estimated_production_impact_cost"].sum().reset_index()
        fig_cost = px.bar(
            plant_cost,
            x="plant_id",
            y="estimated_production_impact_cost",
            color="plant_id",
            text_auto="$,.0f",
            color_discrete_sequence=["#3b82f6", "#10b981", "#8b5cf6"],
            labels={"estimated_production_impact_cost": "Total Exposure ($)", "plant_id": "Facility"}
        )
        fig_cost.update_layout(**get_plotly_theme(), height=340)
        st.plotly_chart(fig_cost, use_container_width=True)

    # 5. Production Order BOM Component Explosion Drilldown
    st.markdown("### 🔬 Production Order BOM Component Drilldown")
    selected_prod_id = st.selectbox(
        "Select Production Order to Inspect Detailed BOM Shortage Breakdown:",
        options=eval_prod_df["production_order_id"].tolist()
    )

    if selected_prod_id:
        p_row = eval_prod_df[eval_prod_df["production_order_id"] == selected_prod_id].iloc[0]
        st.markdown(f"**Order:** `{p_row['production_order_id']}` | **Product:** `{p_row['product_id']}` | **Plant:** `{p_row['plant_id']}` | **Status:** `{p_row['risk_level']}`")
        
        shortages = p_row.get("shortage_details", [])
        if shortages:
            st.dataframe(pd.DataFrame(shortages), use_container_width=True)
        else:
            st.success("✅ 100% Kit Readiness: All required BOM materials are available in sufficient quantities at this plant facility.")

    # Governance Notice
    st.markdown("""
    <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 6px; font-size: 0.8rem; color: #475569; border: 1px solid #e2e8f0; margin-top: 20px;">
        <strong>Methodological Clarity:</strong> Production risks represent <em>material-availability risks</em> derived from current BOM consumption 
        versus verified warehouse reserves and supplier delivery commitments. They do not model intra-plant machine tool wear or maintenance breakdowns.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
