"""
ChainGuard AI - Strategy Cost Comparison Module
Evaluates and compares operational mitigation strategies for material shortages:
Expedite PO, Alternative Supplier, Inter-Plant Transfer, Approved Substitute, Reschedule.
Calculates costs, lead times, recovered volume, residual shortage, and decision tradeoffs.
"""

import pandas as pd
import numpy as np

def evaluate_mitigation_strategies(material_id, shortage_qty, target_date_days=10, unit_cost=45.0, has_alternative=True):
    """
    Simulates 5 distinct operational strategies to resolve a component shortage:
      Option A: Expedite Existing PO via Air Freight
      Option B: Spot Purchase from Pre-Qualified Alternative Supplier
      Option C: Inter-Plant Regional Stock Transfer
      Option D: Activate Approved Technical Substitute Material
      Option E: Reschedule Production Order & Accept Customer Delay
    """
    qty = max(shortage_qty, 50)
    
    strategies = [
        {
            "strategy_id": "OPT-A",
            "strategy_name": "Expedite Existing PO (Air Freight)",
            "description": "Upgrade sea/rail PO shipment to dedicated express air cargo with customs fast-tracking.",
            "cost_breakdown": {
                "base_freight_surcharge": round(qty * 4.5, 2),
                "expedite_expediting_fee": 1500.0,
                "handling": 500.0
            },
            "total_estimated_cost": round(qty * 4.5 + 2000.0, 2),
            "lead_time_days": 4,
            "quantity_recovered": qty,
            "residual_shortage": 0,
            "feasibility": "High" if target_date_days >= 4 else "Moderate",
            "operational_dependencies": "Requires carrier air cargo capacity confirmation within 12 hours.",
            "risk_reduction_score": 90,
            "tradeoff_verdict": "Fastest recovery with zero residual shortage, but carries high per-unit logistics premium."
        },
        {
            "strategy_id": "OPT-B",
            "strategy_name": "Secondary Alternative Supplier Purchase",
            "description": "Issue emergency spot purchase order to secondary certified supplier.",
            "cost_breakdown": {
                "unit_cost_premium_15pct": round(qty * unit_cost * 0.15, 2),
                "expedited_tooling_set_up": 2200.0,
                "freight": 1200.0
            },
            "total_estimated_cost": round((qty * unit_cost * 0.15) + 3400.0, 2),
            "lead_time_days": 8,
            "quantity_recovered": int(round(qty * 0.90)), # 90% allocation
            "residual_shortage": int(round(qty * 0.10)),
            "feasibility": "High" if target_date_days >= 8 else "Low",
            "operational_dependencies": "Requires active commercial NDA and pre-approved quality certification.",
            "risk_reduction_score": 75,
            "tradeoff_verdict": "Secures majority of required volume; protects against primary vendor total failure."
        },
        {
            "strategy_id": "OPT-C",
            "strategy_name": "Inter-Plant Regional Stock Transfer",
            "description": "Transfer surplus safety stock from sister manufacturing facility (PL-EAST/SOUTH).",
            "cost_breakdown": {
                "cross_dock_logistics": 1800.0,
                "warehouse_pick_pack": 600.0,
                "handling": 400.0
            },
            "total_estimated_cost": 2800.0,
            "lead_time_days": 3,
            "quantity_recovered": int(round(qty * 0.85)), # depends on donor plant surplus
            "residual_shortage": int(round(qty * 0.15)),
            "feasibility": "High" if target_date_days >= 3 else "Moderate",
            "operational_dependencies": "Donor plant must confirm stock reservation without creating secondary stockouts.",
            "risk_reduction_score": 85,
            "tradeoff_verdict": "Most cost-effective immediate bridge solution; relies on existing internal capital."
        },
        {
            "strategy_id": "OPT-D",
            "strategy_name": "Approved Engineering Substitute Material",
            "description": "Switch BOM consumption to approved alternative component listed in engineering specs.",
            "cost_breakdown": {
                "engineering_validation_fee": 1200.0,
                "scrap_setup_adjustment": 800.0,
                "unit_variance": round(qty * max(0.0, (unit_cost * 0.05)), 2)
            },
            "total_estimated_cost": round(2000.0 + qty * (unit_cost * 0.05), 2),
            "lead_time_days": 2 if has_alternative else 21,
            "quantity_recovered": qty if has_alternative else 0,
            "residual_shortage": 0 if has_alternative else qty,
            "feasibility": "High" if has_alternative else "Unfeasible (No Approved Alternative)",
            "operational_dependencies": "Quality & Technical Director sign-off required prior to production release.",
            "risk_reduction_score": 80 if has_alternative else 10,
            "tradeoff_verdict": "Highly viable if substitute is pre-approved in BOM; otherwise requires lengthy validation."
        },
        {
            "strategy_id": "OPT-E",
            "strategy_name": "Reschedule Production Order & Absorb Delay",
            "description": "Postpone production start date until standard supplier delivery arrives.",
            "cost_breakdown": {
                "idle_line_capacity_cost": 1200.0 * max(1, (14 - target_date_days)),
                "customer_late_sla_penalty": round(qty * unit_cost * 0.25, 2),
                "rescheduling_admin": 800.0
            },
            "total_estimated_cost": round((1200.0 * max(1, (14 - target_date_days))) + (qty * unit_cost * 0.25) + 800.0, 2),
            "lead_time_days": 14,
            "quantity_recovered": 0,
            "residual_shortage": qty,
            "feasibility": "Low (Breaches Customer SLA)",
            "operational_dependencies": "Requires commercial approval from VP of Sales and plant manager.",
            "risk_reduction_score": 20,
            "tradeoff_verdict": "Zero procurement spend, but inflicts significant financial and reputational customer penalties."
        }
    ]

    df_strat = pd.DataFrame(strategies)
    
    # Identify Recommended Preferred Strategy
    # Rank based on: Feasibility, Time to Availability <= Target Days, and Lowest Cost
    viable = df_strat[df_strat["feasibility"].str.contains("High|Moderate", case=False)].copy()
    if not viable.empty:
        # Prefer strategy with residual_shortage == 0 and lowest cost
        viable["sort_key"] = viable["residual_shortage"] * 10000 + viable["total_estimated_cost"]
        preferred_id = viable.sort_values("sort_key").iloc[0]["strategy_id"]
    else:
        preferred_id = "OPT-A"

    df_strat["is_recommended"] = df_strat["strategy_id"] == preferred_id
    return df_strat
