"""
ChainGuard AI - Production Disruption Analysis Module
Evaluates BOM material requirements against plant stock and incoming purchase orders,
identifying production lines at risk of delay, shortage windows, and idle-time exposure.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def evaluate_production_material_risk(prod_df, bom_df, inv_df, po_df=None):
    """
    Connects planned production orders to BOM component needs,
    cross-references against available plant stock and incoming PO deliveries,
    and calculates shortage quantities and delay windows.
    """
    if prod_df is None or prod_df.empty or bom_df is None or bom_df.empty or inv_df is None or inv_df.empty:
        return pd.DataFrame(), {}

    # Inventory lookup: net available stock per plant & material
    inv_lookup = {}
    for _, row in inv_df.iterrows():
        key = (str(row["plant_id"]).strip(), str(row["material_id"]).strip())
        net_stock = max(0.0, float(row.get("current_stock", 0)) - float(row.get("reserved_stock", 0)))
        inv_lookup[key] = net_stock

    # Incoming PO lookup: earliest promised delivery date & quantity
    po_incoming = {}
    if po_df is not None and not po_df.empty:
        open_pos = po_df[po_df["actual_delivery_date"].isna() | (po_df["actual_delivery_date"] == "")].copy()
        if "promised_delivery_date" in open_pos.columns:
            open_pos["promised_dt"] = pd.to_datetime(open_pos["promised_delivery_date"], errors="coerce")
            for m_id in open_pos["material_id"].dropna().unique():
                m_records = open_pos[open_pos["material_id"] == m_id].sort_values("promised_dt")
                if not m_records.empty:
                    earliest_dt = m_records.iloc[0]["promised_dt"]
                    tot_qty = m_records["quantity_ordered"].sum()
                    po_incoming[str(m_id).strip()] = {
                        "earliest_date": earliest_dt,
                        "earliest_str": earliest_dt.strftime("%Y-%m-%d") if pd.notna(earliest_dt) else "Unknown",
                        "incoming_qty": tot_qty
                    }

    # Evaluate each production order
    evaluated_orders = []

    for _, p_row in prod_df.iterrows():
        p_id = str(p_row["production_order_id"]).strip()
        product = str(p_row["product_id"]).strip()
        plant = str(p_row["plant_id"]).strip()
        qty_planned = float(p_row.get("planned_quantity", 0))
        status = str(p_row.get("production_status", "Scheduled"))
        
        start_dt_str = str(p_row.get("planned_start_date", ""))
        try:
            start_dt = pd.to_datetime(start_dt_str)
        except Exception:
            start_dt = datetime.now()

        # Find BOM requirements for this product
        p_bom = bom_df[bom_df["product_id"] == product]
        if p_bom.empty:
            # Fallback to single material specified in row if BOM match missing
            spec_mat = str(p_row.get("material_id", "MAT-101")).strip()
            qty_req = float(p_row.get("material_quantity_required", qty_planned))
            p_bom = pd.DataFrame([{
                "product_id": product,
                "material_id": spec_mat,
                "quantity_required_per_unit": qty_req / max(qty_planned, 1),
                "material_criticality": "Critical",
                "approved_alternative_material": "None"
            }])

        order_shortages = []
        max_delay_days = 0
        critical_shortage_found = False
        earliest_restock_date = "Sufficient On-Hand"

        for _, b_row in p_bom.iterrows():
            m_id = str(b_row["material_id"]).strip()
            per_unit = float(b_row["quantity_required_per_unit"])
            mat_crit = str(b_row["material_criticality"])
            alt_mat = str(b_row.get("approved_alternative_material", "None"))
            total_req = qty_planned * per_unit

            avail_stock = inv_lookup.get((plant, m_id), 0.0)
            shortage = max(0.0, total_req - avail_stock)

            if shortage > 0:
                # Material has shortage
                po_info = po_incoming.get(m_id, None)
                if po_info and pd.notna(po_info["earliest_date"]):
                    replenish_dt = po_info["earliest_date"]
                    replenish_str = po_info["earliest_str"]
                    # Calculate delay window
                    delay_days = max(0, (replenish_dt - start_dt).days)
                else:
                    replenish_str = "No Open PO on Order"
                    delay_days = 25 # Estimated lead time penalty
                
                if delay_days > max_delay_days:
                    max_delay_days = delay_days
                    earliest_restock_date = replenish_str

                if mat_crit in ["Critical", "High"]:
                    critical_shortage_found = True

                order_shortages.append({
                    "material_id": m_id,
                    "criticality": mat_crit,
                    "required": total_req,
                    "available": avail_stock,
                    "shortage": shortage,
                    "alternative": alt_mat,
                    "replenishment_date": replenish_str,
                    "delay_days": delay_days
                })

        # Determine Production Order Risk Level
        if len(order_shortages) == 0:
            risk_level = "Ready / Low Risk"
            sugg_mitigation = "Standard schedule; all materials available on-site."
            impact_cost = 0.0
        elif critical_shortage_found and max_delay_days > 0:
            risk_level = "Critical Shortage - Delay Imminent"
            sugg_mitigation = "Expedite pending PO via air freight or transfer from regional plant."
            # Estimate daily idle cost: $1,200/day
            impact_cost = max_delay_days * 1200.0 + (qty_planned * 15.0)
        elif len(order_shortages) > 0 and max_delay_days > 0:
            risk_level = "Moderate Material Risk"
            sugg_mitigation = "Review buffer stock or activate approved alternative material."
            impact_cost = max_delay_days * 600.0
        else:
            risk_level = "Minor Buffer Depletion"
            sugg_mitigation = "Monitor incoming deliveries closely."
            impact_cost = 0.0

        evaluated_orders.append({
            "production_order_id": p_id,
            "product_id": product,
            "plant_id": plant,
            "planned_start_date": start_dt.strftime("%Y-%m-%d"),
            "planned_quantity": int(qty_planned),
            "production_status": status,
            "risk_level": risk_level,
            "shortage_count": len(order_shortages),
            "potential_delay_days": max_delay_days,
            "expected_replenishment_date": earliest_restock_date,
            "estimated_production_impact_cost": round(impact_cost, 2),
            "suggested_mitigation": sugg_mitigation,
            "shortage_details": order_shortages
        })

    df_eval = pd.DataFrame(evaluated_orders)
    
    summary = {
        "total_production_orders": len(df_eval),
        "orders_at_risk": len(df_eval[df_eval["risk_level"].str.contains("Critical|Moderate", case=False)]),
        "critical_orders": len(df_eval[df_eval["risk_level"].str.contains("Critical", case=False)]),
        "total_impact_cost": round(df_eval["estimated_production_impact_cost"].sum(), 2)
    }

    return df_eval, summary
