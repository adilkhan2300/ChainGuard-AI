"""
ChainGuard AI - Reporting and Export Module
Generates professional PDF audit reports using ReportLab and multi-sheet Excel workbooks.
"""

import io
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

def generate_pdf_report(
    alerts_df,
    supplier_metrics_df,
    inv_metrics_df,
    prod_metrics_df,
    financial_summary,
    executive_summary_text=""
):
    """
    Builds a multi-page, executive-grade PDF operations report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e3a8a"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4b5563"),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1f2937"),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#374151")
    )
    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1f2937")
    )
    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    story = []

    # Title & Header
    story.append(Paragraph("ChainGuard AI — Supply Chain Resilience & Disruption Intelligence", title_style))
    report_time = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
    story.append(Paragraph(f"Executive Operations & Risk Intelligence Audit | Generated: {report_time}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # 1. Executive Summary Box
    story.append(Paragraph("1. Executive Summary & Financial Exposure", h2_style))
    tot_exposure = financial_summary.get("total_financial_exposure", 0.0)
    idle_loss = financial_summary.get("idle_capacity_losses", 0.0)
    sla_pen = financial_summary.get("sla_delay_penalties", 0.0)
    freight_spend = financial_summary.get("expedited_freight_spend", 0.0)

    summary_p = f"""
    This executive audit consolidates empirical data across active suppliers, inventory reserves,
    production schedules, and multimodal transportation records. The enterprise currently faces
    an aggregate disruption exposure of <b>${tot_exposure:,.2f}</b>, driven by <b>${idle_loss:,.2f}</b>
    in potential plant idle capacity, <b>${sla_pen:,.2f}</b> in customer SLA delay penalties, and
    <b>${freight_spend:,.2f}</b> in premium freight logistics.
    """
    story.append(Paragraph(summary_p, body_style))
    story.append(Spacer(1, 8))

    # Financial Exposure Table
    fin_data = [
        [Paragraph("Cost Driver", table_header_style), Paragraph("Category", table_header_style), Paragraph("Impact ($)", table_header_style)],
        [Paragraph("Manufacturing Plant Idle Losses", table_cell_style), Paragraph("Model-Based Estimate", table_cell_style), Paragraph(f"${idle_loss:,.2f}", table_cell_style)],
        [Paragraph("Customer SLA Delay Penalties", table_cell_style), Paragraph("Model-Based Estimate", table_cell_style), Paragraph(f"${sla_pen:,.2f}", table_cell_style)],
        [Paragraph("Expedited Premium Air Freight", table_cell_style), Paragraph("Actual Recorded", table_cell_style), Paragraph(f"${freight_spend:,.2f}", table_cell_style)],
        [Paragraph("Excess Inventory Carrying Surcharge", table_cell_style), Paragraph("Calculated Metric", table_cell_style), Paragraph(f"${financial_summary.get('excess_holding_cost', 0):,.2f}", table_cell_style)],
        [Paragraph("Total Disruption Financial Exposure", table_header_style), Paragraph("Comprehensive Index", table_header_style), Paragraph(f"${tot_exposure:,.2f}", table_header_style)]
    ]
    fin_table = Table(fin_data, colWidths=[240, 160, 130])
    fin_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#1f2937")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 14))

    # 2. Priority Active Risk Alerts
    story.append(Paragraph("2. Prioritized Supply Chain Risk Alerts", h2_style))
    if alerts_df is not None and not alerts_df.empty:
        alert_rows = [
            [Paragraph("Alert ID", table_header_style), Paragraph("Category", table_header_style), Paragraph("Affected Entity", table_header_style), Paragraph("Severity", table_header_style), Paragraph("Exposure ($)", table_header_style)]
        ]
        for _, alt in alerts_df.head(6).iterrows():
            sev = str(alt.get("risk_severity", "High"))
            alert_rows.append([
                Paragraph(str(alt.get("alert_id", "")), table_cell_style),
                Paragraph(str(alt.get("risk_category", "")), table_cell_style),
                Paragraph(str(alt.get("affected_entity", ""))[:35] + "...", table_cell_style),
                Paragraph(sev, table_cell_style),
                Paragraph(f"${float(alt.get('estimated_financial_exposure', 0)):,.2f}", table_cell_style)
            ])
        alt_table = Table(alert_rows, colWidths=[80, 110, 190, 65, 85])
        alt_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#b91c1c")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4)
        ]))
        story.append(alt_table)
    story.append(Spacer(1, 14))

    # 3. Supplier Risk Highlights
    story.append(Paragraph("3. High-Risk Supplier Performance Rankings", h2_style))
    if supplier_metrics_df is not None and not supplier_metrics_df.empty:
        top_sups = supplier_metrics_df.sort_values("supplier_risk_score", ascending=False).head(5)
        sup_rows = [
            [Paragraph("Supplier Name", table_header_style), Paragraph("Location", table_header_style), Paragraph("OTD Rate", table_header_style), Paragraph("Avg Delay", table_header_style), Paragraph("Risk Score", table_header_style), Paragraph("Level", table_header_style)]
        ]
        for _, s in top_sups.iterrows():
            otd = float(s.get("on_time_delivery_rate", 0)) * 100.0
            sup_rows.append([
                Paragraph(str(s.get("supplier_name", ""))[:25], table_cell_style),
                Paragraph(str(s.get("supplier_location", "")), table_cell_style),
                Paragraph(f"{otd:.1f}%", table_cell_style),
                Paragraph(f"{float(s.get('avg_delay_days', 0)):.1f}d", table_cell_style),
                Paragraph(f"{float(s.get('supplier_risk_score', 0)):.1f}", table_cell_style),
                Paragraph(str(s.get("risk_level", "Medium")), table_cell_style)
            ])
        s_table = Table(sup_rows, colWidths=[140, 110, 70, 60, 70, 80])
        s_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3)
        ]))
        story.append(s_table)
    story.append(Spacer(1, 14))

    # 4. Critical Stockouts & Production Impact
    story.append(Paragraph("4. Inventory Exposure & Manufacturing Impact", h2_style))
    if inv_metrics_df is not None and not inv_metrics_df.empty:
        crit_inv = inv_metrics_df[inv_metrics_df["risk_severity"] == "Critical"].head(5)
        inv_rows = [
            [Paragraph("Material ID", table_header_style), Paragraph("Material Name", table_header_style), Paragraph("Plant", table_header_style), Paragraph("Coverage", table_header_style), Paragraph("Stockout Date", table_header_style)]
        ]
        for _, inv in crit_inv.iterrows():
            cov = float(inv.get("days_of_coverage", 0))
            inv_rows.append([
                Paragraph(str(inv.get("material_id", "")), table_cell_style),
                Paragraph(str(inv.get("material_name", ""))[:25], table_cell_style),
                Paragraph(str(inv.get("plant_id", "")), table_cell_style),
                Paragraph(f"{cov:.1f} days", table_cell_style),
                Paragraph(str(inv.get("projected_stockout_date", "TBD")), table_cell_style)
            ])
        i_table = Table(inv_rows, colWidths=[80, 180, 80, 80, 110])
        i_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#b45309")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3)
        ]))
        story.append(i_table)
    story.append(Spacer(1, 14))

    # 5. Methodological Notes
    story.append(Paragraph("5. Methodology, Data Limitations & Governance", h2_style))
    method_text = """
    <b>Analytical Grounding:</b> Risk scores represent structured multi-factor heuristic evaluations
    derived from documented contractual lead times, actual ERP delivery receipts, and empirical demand
    variability. Machine learning predictions are trained on leak-free order features (order date, volume,
    supplier score) and evaluated with Stratified Train/Test splits. Calculations do not assume live satellite
    tracking or unverified supplier solvency.
    """
    story.append(Paragraph(method_text, body_style))

    doc.build(story)
    return buffer.getvalue()

def generate_multi_tab_excel(data_dict, calculated_dict):
    """
    Exports a comprehensive multi-tab Excel workbook containing all raw datasets
    plus enriched calculations.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Calculated tabs
        for name, df in calculated_dict.items():
            if df is not None and not df.empty:
                sheet = f"CALC_{name}"[:31]
                # Avoid non-serializable objects in columns
                clean_df = df.copy()
                for col in clean_df.columns:
                    if clean_df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        clean_df[col] = clean_df[col].astype(str)
                clean_df.to_excel(writer, sheet_name=sheet, index=False)

        # Raw data tabs
        for name, df in data_dict.items():
            if df is not None and not df.empty:
                clean_df = df.copy()
                for col in clean_df.columns:
                    if clean_df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        clean_df[col] = clean_df[col].astype(str)
                clean_df.to_excel(writer, sheet_name=f"RAW_{name}"[:31], index=False)

    return output.getvalue()
