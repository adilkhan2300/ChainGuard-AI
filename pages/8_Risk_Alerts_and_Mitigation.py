"""
ChainGuard AI - Page 8: Risk Alerts and Mitigation Engine
Displays standardized 8-point structured risk alerts and executes
the LLM-powered mitigation recommendation engine.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.ui_components import (
    apply_custom_styles, render_header, render_alert,
    get_badge
)
from modules.supplier_risk import calculate_supplier_metrics
from modules.inventory_analysis import calculate_inventory_metrics
from modules.production_risk import evaluate_production_material_risk
from modules.transportation_analysis import analyze_transportation_performance
from modules.financial_analysis import compute_financial_impact_breakdown
from modules.risk_scoring import generate_integrated_risk_alerts
from modules.mitigation_engine import generate_rule_based_mitigations
from modules.llm_recommendations import generate_llm_executive_synthesis

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Integrated Risk Alerts & Mitigation Engine",
        subtitle="Operational risk diagnostics synthesized into actionable containment playbooks with team assignments and financial impact"
    )

    sups_df = data_dict.get("suppliers", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())
    inv_df = data_dict.get("inventory", pd.DataFrame())
    prod_df = data_dict.get("production", pd.DataFrame())
    trans_df = data_dict.get("transportation", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())

    if inv_df.empty:
        st.warning("Insufficient data to generate integrated risk alerts.")
        return

    # Compute dependencies
    sup_metrics = calculate_supplier_metrics(sups_df, pos_df, bom_df)
    inv_metrics = calculate_inventory_metrics(inv_df, pos_df)
    prod_eval, _ = evaluate_production_material_risk(prod_df, bom_df, inv_metrics, pos_df)
    _, fin_summary = compute_financial_impact_breakdown(inv_metrics, prod_eval, pos_df, trans_df)
    alerts_df = generate_integrated_risk_alerts(inv_metrics, sup_metrics, prod_eval, trans_df)

    # 1. Executive LLM Briefing Section
    st.markdown("### 🤖 LLM-Powered Executive Risk Briefing")
    
    col_k1, col_k2 = st.columns([3, 1])
    with col_k1:
        api_key_input = st.text_input("OpenAI API Key (Optional — leaves blank to use deterministic rule-based engine):", type="password")
    with col_k2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        gen_btn = st.button("✨ Generate AI Briefing", use_container_width=True)

    if gen_btn or "llm_synthesis" not in st.session_state:
        with st.spinner("Synthesizing empirical supply chain risk diagnostics..."):
            synthesis_text, model_badge = generate_llm_executive_synthesis(alerts_df, fin_summary, api_key=api_key_input)
            st.session_state["llm_synthesis"] = (synthesis_text, model_badge)

    synthesis_text, model_badge = st.session_state["llm_synthesis"]
    st.caption(f"🧠 Synthesis Engine: **{model_badge}**")
    st.markdown(f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 22px; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); color: #1e293b;">
        {synthesis_text}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; height: 1px; background: #e2e8f0; margin: 24px 0;' />", unsafe_allow_html=True)

    # 2. Structured 8-Point Risk Alerts Master Feed
    st.markdown("### 🚨 Active Standardized Risk Alerts")
    st.write("All alerts are formulated with 8 mandatory operational dimensions:")

    if alerts_df.empty:
        st.success("No critical or elevated risk alerts detected across current operational data.")
    else:
        # Filters for Alerts
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            cat_filter = st.multiselect(
                "Filter Alert Category:",
                options=alerts_df["risk_category"].unique().tolist(),
                default=alerts_df["risk_category"].unique().tolist()
            )
        with f_col2:
            sev_filter = st.multiselect(
                "Filter Severity Level:",
                options=alerts_df["risk_severity"].unique().tolist(),
                default=alerts_df["risk_severity"].unique().tolist()
            )

        filtered_alerts = alerts_df.copy()
        if cat_filter:
            filtered_alerts = filtered_alerts[filtered_alerts["risk_category"].isin(cat_filter)]
        if sev_filter:
            filtered_alerts = filtered_alerts[filtered_alerts["risk_severity"].isin(sev_filter)]

        # Display Cards for Each Alert
        for _, alt in filtered_alerts.iterrows():
            sev = alt["risk_severity"]
            sev_color = "#ef4444" if sev == "Critical" else "#f97316"
            
            with st.container():
                st.markdown(f"""
                <div style="background: #ffffff; border-left: 5px solid {sev_color}; border-radius: 8px; padding: 16px 20px; margin-bottom: 14px; border-top: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <span style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">[{alt['alert_id']}] {alt['affected_entity']}</span>
                            <span style="margin-left: 10px; font-size: 0.8rem; background: #eff6ff; color: #2563eb; padding: 2px 8px; border-radius: 4px; border: 1px solid #bfdbfe;">{alt['risk_category']}</span>
                        </div>
                        <div style="font-weight: 700; color: {sev_color}; font-size: 0.9rem;">
                            SEVERITY: {sev.upper()} (Risk Index: {alt['risk_score']:.0f}/100)
                        </div>
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;">
                        <strong>Supporting Evidence:</strong> {alt['supporting_evidence']}
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;">
                        <strong>Expected Timing:</strong> {alt['expected_timing']} | 
                        <strong>Financial Exposure:</strong> <span style="color: #dc2626; font-weight: 600;">${alt['estimated_financial_exposure']:,.2f}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #334155; margin-bottom: 6px;">
                        <strong>Operational Consequences:</strong> {alt['operational_consequences']}
                    </div>
                    <div style="font-size: 0.88rem; color: #166534; background: #f0fdf4; padding: 6px 10px; border-radius: 6px; border: 1px solid #bbf7d0; margin-bottom: 6px;">
                        <strong>Recommended Mitigation:</strong> {alt['recommended_mitigation']}
                    </div>
                    <div style="font-size: 0.78rem; color: #64748b; font-style: italic;">
                        <strong>Data Confidence & Limitations:</strong> {alt['data_confidence']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; height: 1px; background: #e2e8f0; margin: 24px 0;' />", unsafe_allow_html=True)

    # 3. Actionable Operational Mitigation Playbooks
    st.markdown("### 📋 Cross-Domain Mitigation Action Playbooks")
    playbooks_df = generate_rule_based_mitigations(alerts_df)
    
    for _, pb in playbooks_df.iterrows():
        with st.expander(f"📌 [{pb['priority']}] {pb['domain']}: {pb['risk_addressed']}"):
            st.markdown(f"**Proposed Operational Action:** {pb['proposed_action']}")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown(f"**Responsible Team:** `{pb['responsible_team']}`")
                st.markdown(f"**Target Deadline:** `{pb['implementation_deadline']}`")
                st.markdown(f"**Estimated Cost:** `{pb['estimated_cost']}`")
            with p_col2:
                st.markdown(f"**Expected Benefit:** {pb['expected_benefit']}")
                st.markdown(f"**Success Monitoring KPI:** `{pb['success_kpi']}`")
                st.markdown(f"**Assumptions & Limitations:** *{pb['assumptions_limitations']}*")

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
