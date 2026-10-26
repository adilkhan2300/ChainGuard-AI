"""
ChainGuard AI - Page 12: Reports & Exports Hub
Generates professional executive PDF reports (using ReportLab),
multi-sheet Excel workbooks (using openpyxl), and CSV data exports.
"""

import streamlit as st
import pandas as pd
import numpy as np

from utils.ui_components import apply_custom_styles, render_header, render_alert
from modules.supplier_risk import calculate_supplier_metrics
from modules.inventory_analysis import calculate_inventory_metrics
from modules.production_risk import evaluate_production_material_risk
from modules.transportation_analysis import analyze_transportation_performance
from modules.financial_analysis import compute_financial_impact_breakdown
from modules.risk_scoring import generate_integrated_risk_alerts
from modules.mitigation_engine import generate_rule_based_mitigations
from modules.reporting import generate_pdf_report, generate_multi_tab_excel

def render_page(data_dict, filters=None):
    apply_custom_styles()
    render_header(
        title="Executive Reports & Data Export Hub",
        subtitle="Generate board-ready PDF audit documents, multi-sheet analytical Excel workbooks, and CSV extracts"
    )

    sups_df = data_dict.get("suppliers", pd.DataFrame())
    pos_df = data_dict.get("purchase_orders", pd.DataFrame())
    inv_df = data_dict.get("inventory", pd.DataFrame())
    prod_df = data_dict.get("production", pd.DataFrame())
    trans_df = data_dict.get("transportation", pd.DataFrame())
    bom_df = data_dict.get("bill_of_materials", pd.DataFrame())

    if inv_df.empty:
        st.warning("Insufficient data available to generate reports.")
        return

    # Compute all enriched datasets
    sup_metrics = calculate_supplier_metrics(sups_df, pos_df, bom_df)
    inv_metrics = calculate_inventory_metrics(inv_df, pos_df)
    prod_eval, _ = evaluate_production_material_risk(prod_df, bom_df, inv_metrics, pos_df)
    _, _, trans_summary = analyze_transportation_performance(trans_df)
    df_cost, fin_summary = compute_financial_impact_breakdown(inv_metrics, prod_eval, pos_df, trans_df)
    alerts_df = generate_integrated_risk_alerts(inv_metrics, sup_metrics, prod_eval, trans_df)
    playbooks_df = generate_rule_based_mitigations(alerts_df)

    # 1. Executive PDF Report Download Section
    st.markdown("### 📄 One-Click Board-Ready PDF Audit Report")
    st.write("Generates a comprehensive executive report formatted with ReportLab containing executive summaries, KPI tables, supplier rankings, inventory exposure, and financial governance notes:")

    c_pdf1, c_pdf2 = st.columns([2, 1])
    with c_pdf1:
        render_alert(
            "<strong>PDF DOCUMENT CONTENTS:</strong> Executive Summary, Financial Cost Breakdown, "
            "High-Priority 8-Point Risk Alerts, Top Supplier Rankings, Critical Stockouts, and "
            "Methodological Governance Notes. Fully formatted for executive distribution.",
            alert_type="info"
        )
    with c_pdf2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(
            alerts_df=alerts_df,
            supplier_metrics_df=sup_metrics,
            inv_metrics_df=inv_metrics,
            prod_metrics_df=prod_eval,
            financial_summary=fin_summary
        )
        st.download_button(
            label="📥 Download Executive PDF Audit (.pdf)",
            data=pdf_bytes,
            file_name="ChainGuard_Executive_Risk_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 2. Master Multi-Tab Excel Workbook
    st.markdown("### 📊 Comprehensive Multi-Tab Master Excel Workbook")
    st.write("Exports raw operational datasets and enriched analytical calculations into an organized multi-sheet Excel file:")

    calc_dict = {
        "Supplier_Rankings": sup_metrics,
        "Inventory_Coverage": inv_metrics,
        "Production_Risk": prod_eval,
        "Risk_Alerts": alerts_df,
        "Cost_Breakdown": df_cost,
        "Mitigation_Playbooks": playbooks_df
    }

    excel_master_bytes = generate_multi_tab_excel(data_dict, calc_dict)
    st.download_button(
        label="📥 Download Master Multi-Tab Excel Workbook (.xlsx)",
        data=excel_master_bytes,
        file_name="ChainGuard_Master_Analytics_Export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    st.markdown("<hr style='border: 0; height: 1px; background: #374151; margin: 24px 0;' />", unsafe_allow_html=True)

    # 3. Individual CSV Dataset Extracts
    st.markdown("### 📑 Individual Analytical CSV Extracts")
    st.write("Download specific tables for external BI (PowerBI, Tableau) or downstream Python modeling:")

    col_csv1, col_csv2, col_csv3 = st.columns(3)

    with col_csv1:
        st.download_button(
            label="📥 Supplier Risk Rankings (.csv)",
            data=sup_metrics.to_csv(index=False).encode("utf-8"),
            file_name="supplier_risk_rankings.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.download_button(
            label="📥 Critical Stockout Alerts (.csv)",
            data=inv_metrics[inv_metrics["risk_severity"] == "Critical"].to_csv(index=False).encode("utf-8"),
            file_name="critical_stockouts.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_csv2:
        st.download_button(
            label="📥 Production Orders at Risk (.csv)",
            data=prod_eval.to_csv(index=False).encode("utf-8"),
            file_name="production_orders_at_risk.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.download_button(
            label="📥 Standardized Risk Alerts (.csv)",
            data=alerts_df.to_csv(index=False).encode("utf-8"),
            file_name="risk_alerts_all.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_csv3:
        st.download_button(
            label="📥 Mitigation Playbooks (.csv)",
            data=playbooks_df.to_csv(index=False).encode("utf-8"),
            file_name="mitigation_action_playbooks.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.download_button(
            label="📥 Financial Cost Breakdown (.csv)",
            data=df_cost.to_csv(index=False).encode("utf-8"),
            file_name="disruption_cost_breakdown.csv",
            mime="text/csv",
            use_container_width=True
        )

if __name__ == "__main__":
    from modules.data_loader import load_default_data
    render_page(load_default_data())
