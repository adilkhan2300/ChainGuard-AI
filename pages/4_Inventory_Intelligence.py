"""
ChainGuard AI - Page 4: Inventory Shortage & Stockout Prediction
Calculates Net Available Stock, Days of Coverage, Reorder Points,
Safety Stock, Projected Stockout Dates, and Incoming Replenishments.
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
from modules.inventory_analysis import (
    calculate_inventory_metrics, calculate_theoretical_safety_stock
)

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Inventory Intelligence & Stockout Prediction",
        subtitle="Predict material stockouts, track buffer coverage, and simulate statistical safety stocks"
    )

    inv_df = data_dict.get("inventory", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())

    if inv_df.empty:
        st.warning("No inventory records found. Please upload inventory.csv or reset demo data.")
        return

    # Compute enriched inventory KPIs
    inv_metrics = calculate_inventory_metrics(inv_df, pos_df)

    # Filter by plant if user requested
    plants = ["All Plants"] + sorted(inv_metrics["plant_id"].dropna().unique().tolist())
    sel_plant = st.selectbox("🏭 Filter by Manufacturing Facility / Warehouse:", plants)
    if sel_plant != "All Plants":
        inv_metrics = inv_metrics[inv_metrics["plant_id"] == sel_plant]

    # 1. Summary Highlights
    crit_count = len(inv_metrics[inv_metrics["risk_severity"] == "Critical"])
    below_rop_count = len(inv_metrics[inv_metrics["inventory_status"] == "Below Reorder Point"])
    overstock_count = len(inv_metrics[inv_metrics["inventory_status"] == "Overstocked / Excess"])
    tot_val = inv_metrics["inventory_value"].sum()

    render_alert(
        f"<strong>STOCKOUT RISK EXPOSURE:</strong> <strong>{crit_count} Critical Stockouts</strong> detected (&lt; 7 days of coverage). "
        f"An additional <strong>{below_rop_count} items</strong> are below their dynamic reorder threshold. "
        f"Total active inventory asset value is <strong>${tot_val:,.2f}</strong>.",
        alert_type="critical" if crit_count > 0 else "info"
    )

    # 2. KPI Summary Boxes
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Critical Stockouts (<7d)", f"{crit_count} SKUs", delta="Imminent Starvation", delta_color="inverse")
    with k2:
        st.metric("Items Below Reorder Point", f"{below_rop_count} SKUs", delta="Needs PO Reorder", delta_color="inverse")
    with k3:
        avg_cov = round(inv_metrics["days_of_coverage"].replace(999.0, np.nan).dropna().mean(), 1)
        st.metric("Average Coverage Days", f"{avg_cov} days", delta="Across Active Materials")
    with k4:
        st.metric("Overstocked / Excess SKUs", f"{overstock_count} SKUs", delta="Ties Up Working Capital")

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 20px 0;' />", unsafe_allow_html=True)

    # 3. Interactive Inventory Master Table
    st.markdown("### 📋 Material Inventory Coverage & Projected Stockout Table")
    
    status_filter = st.multiselect(
        "Filter by Inventory Status:",
        options=["Critical Stockout Risk", "Below Reorder Point", "Optimal / Healthy", "Overstocked / Excess"],
        default=["Critical Stockout Risk", "Below Reorder Point"]
    )
    
    table_df = inv_metrics[inv_metrics["inventory_status"].isin(status_filter)] if status_filter else inv_metrics

    display_cols = [
        "material_id", "material_name", "plant_id", "current_stock",
        "reserved_stock", "net_available_stock", "average_daily_demand",
        "days_of_coverage", "safety_stock", "reorder_point",
        "projected_stockout_date", "next_replenishment_date", "inventory_status"
    ]

    st.dataframe(
        table_df[display_cols].sort_values("days_of_coverage", ascending=True),
        column_config={
            "days_of_coverage": st.column_config.NumberColumn("Coverage (Days)", format="%.1f"),
            "net_available_stock": st.column_config.NumberColumn("Net Avail Stock", format="%.0f"),
            "average_daily_demand": st.column_config.NumberColumn("Daily Demand", format="%.1f")
        },
        use_container_width=True,
        height=320
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 4. Visual Diagnostics
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("#### Days of Inventory Coverage (Top 12 Most Vulnerable SKUs)")
        chart_data = inv_metrics.sort_values("days_of_coverage", ascending=True).head(12)
        fig_cov = px.bar(
            chart_data,
            x="days_of_coverage",
            y="material_id",
            orientation="h",
            color="inventory_status",
            hover_name="material_name",
            color_discrete_map={
                "Critical Stockout Risk": "#ef4444",
                "Below Reorder Point": "#f97316",
                "Optimal / Healthy": "#10b981",
                "Overstocked / Excess": "#3b82f6"
            },
            labels={"days_of_coverage": "Days of Coverage", "material_id": "Material SKU"}
        )
        fig_cov.add_vline(x=7.0, line_dash="dash", line_color="#ef4444", annotation_text="Critical (7d)")
        fig_cov.add_vline(x=14.0, line_dash="dot", line_color="#f59e0b", annotation_text="Target Buffer (14d)")
        fig_cov.update_layout(**get_plotly_theme(), height=360)
        st.plotly_chart(fig_cov, use_container_width=True)

    with c_right:
        st.markdown("#### Inventory Value Distribution by Plant Facility")
        fig_val = px.pie(
            inv_metrics,
            values="inventory_value",
            names="plant_id",
            hole=0.45,
            color_discrete_sequence=["#3b82f6", "#10b981", "#8b5cf6"]
        )
        fig_val.update_layout(**get_plotly_theme(), height=360)
        st.plotly_chart(fig_val, use_container_width=True)

    # 5. Interactive Dynamic Safety Stock Calculator
    st.markdown("### 🧮 Interactive Dynamic Safety Stock Calculator")
    st.write("Evaluate how demand variance, supplier lead times, and required service levels impact theoretical safety stock requirements:")

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        calc_d = st.number_input("Average Daily Demand (units)", value=25.0, min_value=1.0, step=5.0)
    with sc2:
        calc_sig_d = st.number_input("Demand Std Dev (units/day)", value=6.0, min_value=0.1, step=1.0)
    with sc3:
        calc_lt = st.number_input("Supplier Lead Time (days)", value=21, min_value=1, step=2)
    with sc4:
        calc_sig_lt = st.number_input("Lead Time Std Dev (days)", value=4.0, min_value=0.0, step=0.5)

    svc_level = st.select_slider(
        "Target Cycle Service Level (Non-Stockout Probability):",
        options=[0.90, 0.95, 0.975, 0.99],
        value=0.95,
        format_func=lambda x: f"{x*100:.1f}% ({'z=1.28' if x==0.90 else 'z=1.65' if x==0.95 else 'z=1.96' if x==0.975 else 'z=2.33'})"
    )

    recommended_ss = calculate_theoretical_safety_stock(calc_d, calc_sig_d, calc_lt, calc_sig_lt, svc_level)
    recommended_rop = int(round((calc_d * calc_lt) + recommended_ss))

    st.success(
        f"**Calculated Statistical Buffer Requirements:** "
        f"Recommended Safety Stock = **{recommended_ss:,} units** | "
        f"Optimal Dynamic Reorder Point (ROP) = **{recommended_rop:,} units** "
        f"(covers {recommended_ss / max(calc_d, 1):.1f} days of buffer protection)."
    )

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
