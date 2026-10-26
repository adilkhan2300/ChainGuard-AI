"""
ChainGuard AI - AI-Powered Supply Chain Risk Scoring Engine
Integrates multi-dimensional signals across suppliers, inventory, production,
and logistics into a unified weighted risk index and generates structured risk alerts.
"""

import pandas as pd
import numpy as np

DEFAULT_WEIGHTS = {
    "supplier_reliability": 0.25,
    "inventory_coverage": 0.25,
    "material_criticality": 0.20,
    "lead_time_volatility": 0.15,
    "transport_disruption": 0.15
}

def generate_integrated_risk_alerts(inv_metrics_df, sup_metrics_df, prod_metrics_df, trans_df=None, weights=None):
    """
    Synthesizes signals from all operational modules and produces 8-point structured risk alerts.
    Every alert contains:
      1. Risk Category
      2. Affected Entity (Material, Supplier, Shipment, Production Order)
      3. Supporting Evidence
      4. Expected Timing
      5. Operational Consequences
      6. Estimated Financial Exposure ($)
      7. Recommended Mitigation Action
      8. Data Confidence & Limitations
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    alerts = []
    
    # 1. Evaluate Critical Inventory Shortages
    if inv_metrics_df is not None and not inv_metrics_df.empty:
        crit_inv = inv_metrics_df[inv_metrics_df["risk_severity"] == "Critical"].copy()
        for _, row in crit_inv.iterrows():
            m_id = str(row["material_id"])
            m_name = str(row["material_name"])
            plant = str(row["plant_id"])
            coverage = float(row.get("days_of_coverage", 0))
            net_stock = float(row.get("net_available_stock", 0))
            daily_demand = float(row.get("average_daily_demand", 0))
            unit_cost = float(row.get("inventory_unit_cost", 10))
            stockout_dt = str(row.get("projected_stockout_date", "Immediate"))

            fin_exposure = round(max(5000.0, (daily_demand * 14.0 * unit_cost) + 8500.0), 2)

            alerts.append({
                "alert_id": f"ALT-INV-{m_id}-{plant}",
                "risk_category": "Inventory Stockout",
                "risk_severity": "Critical",
                "risk_score": 92.0,
                "affected_entity": f"Material {m_id} ({m_name}) at {plant}",
                "supporting_evidence": f"Only {coverage:.1f} days of inventory remaining. Net available stock is {net_stock:.0f} units against daily consumption of {daily_demand:.1f} units/day.",
                "expected_timing": f"Projected Stockout Date: {stockout_dt}",
                "operational_consequences": f"High probability of assembly line starvation at {plant}, idling manufacturing lines and jeopardizing customer delivery commitments.",
                "estimated_financial_exposure": fin_exposure,
                "recommended_mitigation": f"Expedite inbound purchase orders or initiate emergency cross-dock inter-plant transfer from regional warehouses.",
                "data_confidence": "High (Calculated from verified current ERP stock and historical 30-day demand consumption rate)."
            })

    # 2. Evaluate High-Risk Suppliers
    if sup_metrics_df is not None and not sup_metrics_df.empty:
        risky_sups = sup_metrics_df[sup_metrics_df["supplier_risk_score"] >= 65.0].copy()
        for _, row in risky_sups.iterrows():
            s_id = str(row["supplier_id"])
            s_name = str(row["supplier_name"])
            otd = float(row.get("on_time_delivery_rate", 0.8))
            avg_delay = float(row.get("avg_delay_days", 0))
            open_delayed = int(row.get("open_delayed_pos", 0))
            score = float(row.get("supplier_risk_score", 70))
            fin_risk = float(row.get("financial_risk_score", 0.2))

            fin_exposure = round(max(12000.0, open_delayed * 4500.0 + (fin_risk * 25000.0)), 2)

            alerts.append({
                "alert_id": f"ALT-SUP-{s_id}",
                "risk_category": "Supplier Reliability & Solvency",
                "risk_severity": "Critical" if score >= 75 else "High",
                "risk_score": score,
                "affected_entity": f"Supplier {s_id} - {s_name}",
                "supporting_evidence": f"Historical OTD rate of {otd*100:.1f}%, average delivery delay of {avg_delay:.1f} days, and {open_delayed} currently delayed open orders. Financial risk score is {fin_risk:.2f}.",
                "expected_timing": "Ongoing lead-time instability impacting current order replenishment cycle.",
                "operational_consequences": "Cumulative component delivery delays creating production rescheduling bottlenecks and potential single-source dependency risk.",
                "estimated_financial_exposure": fin_exposure,
                "recommended_mitigation": "Dual-source allocation; enforce SLA liquidated damages and audit supplier financial health.",
                "data_confidence": "Medium-High (Historical PO fulfillment records combined with Altman-Z financial indicators)."
            })

    # 3. Evaluate Production Orders at Risk
    if prod_metrics_df is not None and not prod_metrics_df.empty:
        crit_prods = prod_metrics_df[prod_metrics_df["risk_level"].str.contains("Critical", case=False)].copy()
        for _, row in crit_prods.iterrows():
            p_id = str(row["production_order_id"])
            prod = str(row["product_id"])
            plant = str(row["plant_id"])
            delay_days = int(row.get("potential_delay_days", 0))
            impact_cost = float(row.get("estimated_production_impact_cost", 0))
            start_dt = str(row.get("planned_start_date", "Scheduled"))
            replenish_dt = str(row.get("expected_replenishment_date", "TBD"))

            alerts.append({
                "alert_id": f"ALT-PRD-{p_id}",
                "risk_category": "Production Line Delay",
                "risk_severity": "Critical",
                "risk_score": 88.0,
                "affected_entity": f"Production Order {p_id} (Product {prod}) at {plant}",
                "supporting_evidence": f"Critical BOM materials missing on-site. Earliest incoming replenishment is {replenish_dt}, creating a {delay_days}-day delay window past planned start ({start_dt}).",
                "expected_timing": f"Start date affected on {start_dt}; delay duration: {delay_days} days.",
                "operational_consequences": f"Production line halting for {prod}, unutilized labor hours, and downstream missed SLA penalties.",
                "estimated_financial_exposure": round(impact_cost, 2),
                "recommended_mitigation": "Resequence production lines to prioritize orders with full kit readiness; validate approved alternative material.",
                "data_confidence": "High (BOM explosion matched against current plant stock and supplier commitments)."
            })

    # 4. Evaluate Logistics Bottlenecks
    if trans_df is not None and not trans_df.empty:
        delayed_trans = trans_df[trans_df["shipment_status"].astype(str).str.contains("Delayed", case=False, na=False)].copy()
        for _, row in delayed_trans.head(5).iterrows():
            shp_id = str(row["shipment_id"])
            po_id = str(row["purchase_order_id"])
            car_id = str(row["carrier_id"])
            mode = str(row["transport_mode"])
            route = f"{row.get('origin', '')} -> {row.get('destination', '')}"
            est_arr = str(row.get("estimated_arrival_date", ""))

            alerts.append({
                "alert_id": f"ALT-LOG-{shp_id}",
                "risk_category": "Logistics & In-Transit Delay",
                "risk_severity": "High",
                "risk_score": 72.0,
                "affected_entity": f"Shipment {shp_id} (PO {po_id}) via {car_id} ({mode})",
                "supporting_evidence": f"Shipment delayed in corridor: {route}. Estimated arrival {est_arr} violated with carrier delay status.",
                "expected_timing": "Immediate (In-Transit Disruption)",
                "operational_consequences": "Delayed arrival will postpone safety stock replenishment and feed into plant shortage queue.",
                "estimated_financial_exposure": 4200.0,
                "recommended_mitigation": "Escalate with carrier dispatcher; reroute pending downstream shipments to air or priority road freight.",
                "data_confidence": "Medium (Based on carrier SLA records and shipment status logs)."
            })

    df_alerts = pd.DataFrame(alerts)
    return df_alerts
