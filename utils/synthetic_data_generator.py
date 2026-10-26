"""
ChainGuard AI - Synthetic Data Generator
Generates realistic, coherent, and relational supply chain datasets with realistic disruption patterns:
- 25 Suppliers with diverse locations, ratings, and financial risk
- 60 Raw Materials / SKUs with BOM mapping to 8 Finished Products
- 150+ Purchase Orders spanning 9 months with real delivery delay patterns
- 35 Production Orders across 3 manufacturing plants
- 120+ Transportation Shipments across Air, Ocean, Road, Rail
- 6+ months of historical demand records with volatility & spikes
- Bill of Materials (BOM) linking products, criticalities, and approved alternatives
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set fixed seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

BASE_DATE = datetime(2026, 1, 1)

def generate_all_datasets(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)

    # ---------------------------------------------------------
    # 1. SUPPLIERS (25 suppliers)
    # ---------------------------------------------------------
    suppliers_data = [
        ("SUP-001", "Apex Microelectronics Corp", "Hsinchu, Taiwan", "Electronics, Semiconductors", 35, 120000, 4.6, 0.15, "Active"),
        ("SUP-002", "Bavaria Precision Alloys", "Munich, Germany", "Metals, Specialty Steel", 28, 85000, 4.8, 0.10, "Active"),
        ("SUP-003", "Pacific Rim Polymers", "Rayong, Thailand", "Plastics, Polymers", 21, 150000, 3.9, 0.32, "Active"),
        ("SUP-004", "Great Lakes Fasteners", "Cleveland, USA", "Hardware, Fasteners", 14, 250000, 4.7, 0.08, "Active"),
        ("SUP-005", "Shenzhen Opto-Tech Ltd", "Shenzhen, China", "Optics, Displays", 30, 95000, 4.1, 0.28, "Active"),
        ("SUP-006", "Nordic Sensor Systems", "Gothenburg, Sweden", "Sensors, Actuators", 25, 60000, 4.9, 0.05, "Active"),
        ("SUP-007", "Bajaj Wire & Cable", "Pune, India", "Wiring, Connectors", 18, 180000, 4.2, 0.22, "Active"),
        ("SUP-008", "Monterrey Stamping & Castings", "Monterrey, Mexico", "Metals, Enclosures", 16, 110000, 4.3, 0.18, "Active"),
        ("SUP-009", "Kyoto Advanced Ceramics", "Kyoto, Japan", "Ceramics, Insulation", 32, 50000, 4.9, 0.06, "Active"),
        ("SUP-010", "Saigon Packaging Solutions", "Ho Chi Minh, Vietnam", "Packaging, Cardboard", 12, 300000, 4.0, 0.25, "Active"),
        ("SUP-011", "Rhine Chemical Specialties", "Frankfurt, Germany", "Chemicals, Adhesives", 24, 75000, 4.5, 0.12, "Active"),
        ("SUP-012", "Delta Power Electronics", "Seoul, South Korea", "Power Supplies, Converters", 28, 90000, 4.4, 0.14, "Active"),
        ("SUP-013", "Atlas Rubber & Gaskets", "Akron, USA", "Gaskets, Seals", 15, 140000, 3.8, 0.40, "Under Review"),
        ("SUP-014", "Wuhan Semiconductor Co", "Wuhan, China", "Semiconductors, ICs", 42, 80000, 3.7, 0.45, "Elevated Risk"),
        ("SUP-015", "Lyon Fluid Systems", "Lyon, France", "Hydraulics, Tubing", 26, 65000, 4.6, 0.11, "Active"),
        ("SUP-016", "Sunbelt Copper & Brass", "Phoenix, USA", "Metals, Non-Ferrous", 17, 130000, 4.2, 0.19, "Active"),
        ("SUP-017", "Taichung Precision Tooling", "Taichung, Taiwan", "Tooling, Hardware", 22, 90000, 4.5, 0.13, "Active"),
        ("SUP-018", "Penang Circuit Assembly", "Penang, Malaysia", "PCBs, SMT Assembly", 27, 105000, 4.3, 0.20, "Active"),
        ("SUP-019", "Katowice Industrial Composites", "Katowice, Poland", "Composites, Resins", 20, 85000, 4.4, 0.16, "Active"),
        ("SUP-020", "Sao Paulo Bio-Polymers", "Campinas, Brazil", "Plastics, Bio-Resins", 30, 70000, 3.6, 0.48, "Elevated Risk"),
        ("SUP-021", "Osaka Battery & Cell Corp", "Osaka, Japan", "Batteries, Energy Storage", 35, 75000, 4.8, 0.09, "Active"),
        ("SUP-022", "Bristol Thermal Management", "Bristol, UK", "Heatsinks, Cooling", 21, 95000, 4.5, 0.15, "Active"),
        ("SUP-023", "Guadalajara Wire Harnesses", "Guadalajara, Mexico", "Harnesses, Looms", 15, 160000, 4.1, 0.26, "Active"),
        ("SUP-024", "Antwerp Logistics Packaging", "Antwerp, Belgium", "Packaging, Crates", 10, 220000, 4.7, 0.07, "Active"),
        ("SUP-025", "Vanguard Resistors & Passives", "Singapore", "Passives, Capacitors", 19, 350000, 4.6, 0.11, "Active")
    ]
    df_suppliers = pd.DataFrame(suppliers_data, columns=[
        "supplier_id", "supplier_name", "supplier_location", "material_categories",
        "contractual_lead_time_days", "supplier_capacity", "quality_rating",
        "financial_risk_score", "supplier_status"
    ])
    df_suppliers.to_csv(os.path.join(output_dir, "suppliers.csv"), index=False)

    # ---------------------------------------------------------
    # 2. FINISHED PRODUCTS & MATERIALS (60 Materials, 8 Products)
    # ---------------------------------------------------------
    # 8 Finished Products:
    # PROD-01: Smart Industrial Controller
    # PROD-02: High-Torque Servo Actuator
    # PROD-03: Edge IoT Gateway Hub
    # PROD-04: Precision Sensor Node
    # PROD-05: Industrial Power Inverter
    # PROD-06: Medical Diagnostic Monitor
    # PROD-07: Robotic Arm Joint Module
    # PROD-08: Autonomous Fleet Telematics Unit

    materials_list = [
        # Electronics / Chips
        ("MAT-101", "ARM Cortex Microcontroller", "Electronics", 45.0, "SUP-001", "SUP-014", "Critical"),
        ("MAT-102", "FPGA Accelerator Chip", "Electronics", 125.0, "SUP-001", None, "Critical"),
        ("MAT-103", "Precision ADC 24-Bit", "Electronics", 18.5, "SUP-001", "SUP-025", "High"),
        ("MAT-104", "Power MOSFET Transistor 100V", "Electronics", 4.2, "SUP-012", "SUP-025", "Medium"),
        ("MAT-105", "Optocoupler Isolation IC", "Electronics", 2.8, "SUP-005", "SUP-025", "Low"),
        ("MAT-106", "Wi-Fi 6 / BLE Module", "Electronics", 14.5, "SUP-001", "SUP-018", "High"),
        ("MAT-107", "Multi-Layer Ceramic Cap 10uF", "Electronics", 0.45, "SUP-025", "SUP-007", "Low"),
        ("MAT-108", "Precision Shunt Resistor 1%", "Electronics", 1.2, "SUP-025", None, "Medium"),
        ("MAT-109", "Flash Memory SPI 128MB", "Electronics", 6.8, "SUP-001", "SUP-014", "High"),
        ("MAT-110", "Linear Voltage Regulator 3.3V", "Electronics", 1.8, "SUP-012", "SUP-001", "Low"),
        
        # Displays & Optics
        ("MAT-111", "7-Inch TFT Touch Display IPS", "Optics", 58.0, "SUP-005", None, "Critical"),
        ("MAT-112", "OLED Status Display 1.3-Inch", "Optics", 12.0, "SUP-005", "SUP-001", "Medium"),
        ("MAT-113", "Optical Diffuser Lens Plate", "Optics", 6.5, "SUP-005", "SUP-009", "Low"),
        
        # Sensors
        ("MAT-114", "6-Axis MEMS IMU Sensor", "Sensors", 22.0, "SUP-006", "SUP-001", "Critical"),
        ("MAT-115", "Digital Pressure Transducer", "Sensors", 38.0, "SUP-006", None, "Critical"),
        ("MAT-116", "RTD Platinum Temp Sensor PT100", "Sensors", 16.5, "SUP-006", "SUP-009", "High"),
        ("MAT-117", "Hall Effect Rotary Sensor", "Sensors", 9.4, "SUP-006", "SUP-012", "Medium"),
        ("MAT-118", "Ultrasonic Distance Sensor", "Sensors", 14.0, "SUP-006", None, "High"),
        
        # Power & Batteries
        ("MAT-119", "LiFePO4 Battery Pack 48V 10Ah", "Energy", 210.0, "SUP-021", None, "Critical"),
        ("MAT-120", "Toroidal Power Transformer 250VA", "Power", 42.0, "SUP-012", "SUP-007", "High"),
        ("MAT-121", "DC-DC Buck Converter Module 24V", "Power", 15.0, "SUP-012", "SUP-001", "Medium"),
        ("MAT-122", "High-Voltage Capacitor Bank", "Power", 28.0, "SUP-025", "SUP-012", "High"),
        
        # Metals & Enclosures
        ("MAT-123", "Extruded Aluminum Enclosure 6061", "Metals", 34.0, "SUP-008", "SUP-002", "High"),
        ("MAT-124", "Die-Cast Zinc Gearbox Housing", "Metals", 26.5, "SUP-008", "SUP-017", "Critical"),
        ("MAT-125", "Stainless Steel 316 Mounting Plate", "Metals", 19.0, "SUP-002", "SUP-008", "Medium"),
        ("MAT-126", "Copper Heat Pipe Heat Sink Assembly", "Metals", 22.5, "SUP-022", "SUP-016", "High"),
        ("MAT-127", "Sheet Metal Chassis Panel", "Metals", 14.0, "SUP-008", "SUP-002", "Low"),
        ("MAT-128", "Hardened Alloy Steel Drive Shaft", "Metals", 31.0, "SUP-002", "SUP-017", "Critical"),
        ("MAT-129", "Brass Bushing Sleeve", "Metals", 5.2, "SUP-016", "SUP-004", "Low"),
        ("MAT-130", "Titanium Fastener Stud M6", "Metals", 8.5, "SUP-002", "SUP-004", "Medium"),

        # Plastics & Polymers
        ("MAT-131", "Flame-Retardant Polycarbonate Bezel", "Plastics", 9.8, "SUP-003", "SUP-020", "Medium"),
        ("MAT-132", "Nylon 66 High-Strength Gear Set", "Plastics", 13.5, "SUP-003", "SUP-019", "High"),
        ("MAT-133", "Silicone Environmental Gasket Seal", "Plastics", 4.5, "SUP-013", "SUP-003", "High"),
        ("MAT-134", "EPDM O-Ring Kit 40-Piece", "Plastics", 3.2, "SUP-013", "SUP-003", "Low"),
        ("MAT-135", "Conductive Elastomer EMI Gasket", "Plastics", 7.8, "SUP-013", None, "Critical"),
        ("MAT-136", "Carbon Fiber Reinforced Bracket", "Plastics", 28.0, "SUP-019", "SUP-003", "High"),

        # Wiring & Connectors
        ("MAT-137", "Automotive Spec Wire Harness Loom", "Wiring", 32.0, "SUP-023", "SUP-007", "Critical"),
        ("MAT-138", "M12 Industrial Circular Connector 8-Pin", "Wiring", 11.5, "SUP-007", "SUP-023", "Medium"),
        ("MAT-139", "Shielded Twisted Pair Cable 100m Reel", "Wiring", 65.0, "SUP-007", "SUP-016", "Medium"),
        ("MAT-140", "Gold-Plated Terminal Header 40-Pin", "Wiring", 3.8, "SUP-007", "SUP-025", "Low"),
        ("MAT-141", "Internal Ribbon Flex Cable FPC", "Wiring", 5.5, "SUP-018", "SUP-007", "Medium"),

        # PCBs & Sub-Assemblies
        ("MAT-142", "6-Layer Rigid-Flex Mainboard PCB", "PCBs", 44.0, "SUP-018", "SUP-001", "Critical"),
        ("MAT-143", "4-Layer Power Supply Board", "PCBs", 22.0, "SUP-018", "SUP-012", "High"),
        ("MAT-144", "Daughterboard Interface Card", "PCBs", 15.0, "SUP-018", None, "Medium"),

        # Ceramics, Chemicals & Adhesives
        ("MAT-145", "Thermal Interface Gap Filler Pad", "Chemicals", 4.2, "SUP-011", "SUP-009", "Medium"),
        ("MAT-146", "Structural Epoxy Adhesive 50ml", "Chemicals", 12.5, "SUP-011", None, "High"),
        ("MAT-147", "Conformal Coating Polyurethane 1L", "Chemicals", 48.0, "SUP-011", "SUP-019", "Medium"),
        ("MAT-148", "Alumina Ceramic Insulator Plate", "Ceramics", 16.0, "SUP-009", "SUP-002", "High"),

        # Hardware & Fasteners
        ("MAT-149", "Socket Head Cap Screws M4 Stainless (100pk)", "Hardware", 8.0, "SUP-004", "SUP-017", "Low"),
        ("MAT-150", "Self-Locking Nylon Nuts M4 (100pk)", "Hardware", 5.5, "SUP-004", "SUP-017", "Low"),
        ("MAT-151", "Precision Ball Bearing 608-2RS", "Hardware", 6.8, "SUP-004", "SUP-002", "Critical"),
        ("MAT-152", "Stainless Helicoil Thread Inserts", "Hardware", 9.0, "SUP-004", None, "Medium"),

        # Packaging & Logistics
        ("MAT-153", "Anti-Static Foam Cushion Inlay", "Packaging", 3.5, "SUP-010", "SUP-024", "Low"),
        ("MAT-154", "Heavy-Duty Corrugated Shipping Box", "Packaging", 4.8, "SUP-010", "SUP-024", "Low"),
        ("MAT-155", "Desiccant Silica Gel Packets 50g", "Packaging", 1.2, "SUP-010", "SUP-024", "Low"),
        ("MAT-156", "Tamper-Evident Security Seal Label", "Packaging", 0.8, "SUP-010", "SUP-024", "Low"),

        # Actuators & Tooling
        ("MAT-157", "Brushless DC Motor Stator Assembly", "Actuators", 78.0, "SUP-017", "SUP-006", "Critical"),
        ("MAT-158", "Harmonic Speed Reducer Gearbox", "Actuators", 160.0, "SUP-017", None, "Critical"),
        ("MAT-159", "Pneumatic Solenoid Valve 24V", "Hydraulics", 35.0, "SUP-015", "SUP-006", "High"),
        ("MAT-160", "Flexible Polyurethane Air Tubing 10m", "Hydraulics", 14.0, "SUP-015", "SUP-003", "Low")
    ]

    # ---------------------------------------------------------
    # 3. BILL OF MATERIALS (BOM)
    # ---------------------------------------------------------
    products = [
        "PROD-01", "PROD-02", "PROD-03", "PROD-04",
        "PROD-05", "PROD-06", "PROD-07", "PROD-08"
    ]

    bom_records = []
    # Explicit mapping of materials to products with quantities & criticality
    product_material_map = {
        "PROD-01": ["MAT-101", "MAT-103", "MAT-107", "MAT-109", "MAT-111", "MAT-123", "MAT-133", "MAT-142", "MAT-145", "MAT-149", "MAT-153", "MAT-154"],
        "PROD-02": ["MAT-104", "MAT-117", "MAT-124", "MAT-128", "MAT-132", "MAT-137", "MAT-143", "MAT-151", "MAT-157", "MAT-158", "MAT-149", "MAT-154"],
        "PROD-03": ["MAT-101", "MAT-106", "MAT-109", "MAT-112", "MAT-123", "MAT-135", "MAT-139", "MAT-142", "MAT-147", "MAT-150", "MAT-154"],
        "PROD-04": ["MAT-103", "MAT-114", "MAT-115", "MAT-116", "MAT-125", "MAT-133", "MAT-138", "MAT-144", "MAT-145", "MAT-150", "MAT-155"],
        "PROD-05": ["MAT-102", "MAT-104", "MAT-108", "MAT-110", "MAT-120", "MAT-122", "MAT-126", "MAT-127", "MAT-135", "MAT-143", "MAT-148"],
        "PROD-06": ["MAT-101", "MAT-102", "MAT-111", "MAT-114", "MAT-119", "MAT-125", "MAT-131", "MAT-135", "MAT-142", "MAT-146", "MAT-153"],
        "PROD-07": ["MAT-117", "MAT-124", "MAT-128", "MAT-136", "MAT-137", "MAT-151", "MAT-157", "MAT-158", "MAT-159", "MAT-160", "MAT-152"],
        "PROD-08": ["MAT-101", "MAT-106", "MAT-114", "MAT-118", "MAT-119", "MAT-121", "MAT-123", "MAT-133", "MAT-137", "MAT-144", "MAT-156"]
    }

    # Material dictionary for lookup
    mat_dict = {m[0]: m for m in materials_list}

    # Alternatives dictionary
    alt_map = {
        "MAT-101": "MAT-102",
        "MAT-103": "MAT-108",
        "MAT-104": "MAT-121",
        "MAT-106": "MAT-144",
        "MAT-107": "MAT-122",
        "MAT-109": "MAT-101",
        "MAT-112": "MAT-111",
        "MAT-114": "MAT-117",
        "MAT-116": "MAT-115",
        "MAT-123": "MAT-125",
        "MAT-124": "MAT-128",
        "MAT-131": "MAT-136",
        "MAT-133": "MAT-134",
        "MAT-137": "MAT-139",
        "MAT-142": "MAT-143",
        "MAT-149": "MAT-150",
        "MAT-153": "MAT-154",
        "MAT-157": "MAT-158",
        "MAT-159": "MAT-160"
    }

    for prod_id, mats in product_material_map.items():
        for m_id in mats:
            m_info = mat_dict[m_id]
            crit = m_info[6]
            alt = alt_map.get(m_id, None)
            qty_req = random.choice([1.0, 2.0, 4.0, 8.0]) if "Fastener" in m_info[1] or "Capacitor" in m_info[1] else random.choice([1.0, 1.0, 2.0])
            bom_records.append({
                "product_id": prod_id,
                "material_id": m_id,
                "quantity_required_per_unit": qty_req,
                "material_criticality": crit,
                "approved_alternative_material": alt if alt else "None"
            })

    df_bom = pd.DataFrame(bom_records)
    df_bom.to_csv(os.path.join(output_dir, "bill_of_materials.csv"), index=False)

    # ---------------------------------------------------------
    # 4. INVENTORY (60 Materials across 3 Plants: PL-NORTH, PL-SOUTH, PL-EAST)
    # ---------------------------------------------------------
    plants = ["PL-NORTH", "PL-SOUTH", "PL-EAST"]
    inv_records = []

    for m in materials_list:
        m_id = m[0]
        m_name = m[1]
        u_cost = m[3]
        crit = m[6]

        # Allocate across plants
        for plant in plants:
            # Plant distribution: PL-NORTH has 50%, PL-SOUTH 30%, PL-EAST 20%
            base_demand = np.random.uniform(5.0, 35.0)
            if plant == "PL-SOUTH":
                base_demand *= 0.6
            elif plant == "PL-EAST":
                base_demand *= 0.4
            
            avg_daily_demand = round(base_demand, 1)
            # Criticality drives lead time and safety stock
            lead_time_days = random.randint(14, 35)
            # Demand std dev
            sigma_d = avg_daily_demand * np.random.uniform(0.15, 0.40)
            z_score = 1.96 if crit in ["Critical", "High"] else 1.64
            safety_stock = int(round(z_score * np.sqrt(lead_time_days) * sigma_d))
            reorder_point = int(round((avg_daily_demand * lead_time_days) + safety_stock))
            
            # Introduce real shortage cases for demo:
            # Specially starve MAT-101, MAT-111, MAT-119, MAT-124, MAT-135 at PL-NORTH and PL-SOUTH
            if m_id in ["MAT-101", "MAT-111", "MAT-119", "MAT-124", "MAT-135"] and plant in ["PL-NORTH", "PL-SOUTH"]:
                current_stock = int(round(avg_daily_demand * np.random.uniform(1.5, 4.0))) # only 2-4 days coverage!
                reserved_stock = int(round(current_stock * 0.6))
            elif m_id in ["MAT-114", "MAT-142", "MAT-151", "MAT-157"] and plant == "PL-NORTH":
                current_stock = int(round(reorder_point * 0.75)) # below ROP
                reserved_stock = int(round(current_stock * 0.4))
            elif m_id in ["MAT-107", "MAT-149", "MAT-154"]: # overstocked materials
                current_stock = int(round(reorder_point * 3.5))
                reserved_stock = int(round(current_stock * 0.1))
            else:
                # normal healthy distribution
                current_stock = int(round(reorder_point * np.random.uniform(1.1, 2.0)))
                reserved_stock = int(round(current_stock * np.random.uniform(0.15, 0.35)))

            inv_records.append({
                "material_id": m_id,
                "material_name": m_name,
                "plant_id": plant,
                "current_stock": current_stock,
                "reserved_stock": reserved_stock,
                "safety_stock": safety_stock,
                "reorder_point": reorder_point,
                "average_daily_demand": avg_daily_demand,
                "inventory_unit_cost": u_cost,
                "inventory_date": (BASE_DATE + timedelta(days=260)).strftime("%Y-%m-%d")
            })

    df_inventory = pd.DataFrame(inv_records)
    df_inventory.to_csv(os.path.join(output_dir, "inventory.csv"), index=False)

    # ---------------------------------------------------------
    # 5. PURCHASE ORDERS (160 POs across 9 months)
    # ---------------------------------------------------------
    po_records = []
    po_counter = 1001

    # Elevated risk suppliers: SUP-014 (Wuhan), SUP-020 (Sao Paulo), SUP-013 (Atlas), SUP-003 (Pacific Rim)
    elevated_suppliers = ["SUP-014", "SUP-020", "SUP-013", "SUP-003"]

    for i in range(165):
        po_id = f"PO-{po_counter}"
        po_counter += 1

        # Select material and its primary supplier
        m = random.choice(materials_list)
        m_id = m[0]
        sup_id = m[4]
        # Occasionally use secondary
        if m[5] and random.random() < 0.25:
            sup_id = m[5]
        
        # Order date between Jan 2026 and Aug 2026
        order_day_offset = random.randint(5, 250)
        order_dt = BASE_DATE + timedelta(days=order_day_offset)

        # Supplier contract lead time
        sup_row = df_suppliers[df_suppliers["supplier_id"] == sup_id].iloc[0]
        std_lead_time = int(sup_row["contractual_lead_time_days"])
        promised_dt = order_dt + timedelta(days=std_lead_time)

        qty_ordered = int(random.choice([100, 250, 500, 1000, 2000, 5000]))
        unit_cost = m[3]

        # Determine status and actual delivery based on order date and supplier risk
        today_ref = BASE_DATE + timedelta(days=260) # late Sept 2026

        if promised_dt < today_ref - timedelta(days=15):
            # Order is in the past -> Delivered or Late Delivered
            is_risky = sup_id in elevated_suppliers
            prob_delay = 0.65 if is_risky else 0.15
            
            if random.random() < prob_delay:
                # Delayed
                delay_days = random.randint(5, 28)
                actual_dt = promised_dt + timedelta(days=delay_days)
                # Shortfall risk
                qty_received = int(round(qty_ordered * (np.random.uniform(0.75, 0.95) if random.random() < 0.3 else 1.0)))
                po_status = "Delivered Late" if qty_received == qty_ordered else "Partially Delivered"
            else:
                # On time or slightly early
                early_late = random.randint(-3, 0)
                actual_dt = promised_dt + timedelta(days=early_late)
                qty_received = qty_ordered
                po_status = "Delivered On-Time"
            
            actual_str = actual_dt.strftime("%Y-%m-%d")
        else:
            # Currently Open or In-Transit
            actual_str = "" # Not yet received
            qty_received = 0
            if promised_dt < today_ref:
                po_status = "Delayed Open"
            else:
                po_status = "Open Confirmed"

        po_records.append({
            "purchase_order_id": po_id,
            "supplier_id": sup_id,
            "material_id": m_id,
            "order_date": order_dt.strftime("%Y-%m-%d"),
            "promised_delivery_date": promised_dt.strftime("%Y-%m-%d"),
            "actual_delivery_date": actual_str,
            "quantity_ordered": qty_ordered,
            "quantity_received": qty_received,
            "unit_cost": unit_cost,
            "purchase_order_status": po_status
        })

    df_po = pd.DataFrame(po_records)
    df_po.to_csv(os.path.join(output_dir, "purchase_orders.csv"), index=False)

    # ---------------------------------------------------------
    # 6. TRANSPORTATION (140 Shipments)
    # ---------------------------------------------------------
    carriers = [
        ("CAR-01", "Maersk Global Freight", "Ocean", 0.08),
        ("CAR-02", "DHL Global Forwarding", "Air", 0.05),
        ("CAR-03", "Kuehne+Nagel Intermodal", "Ocean", 0.12),
        ("CAR-04", "DB Schenker Overland", "Road", 0.10),
        ("CAR-05", "FedEx Supply Chain Logistics", "Air", 0.06),
        ("CAR-06", "Trans-Eurasia Rail Express", "Rail", 0.22), # higher delay rate
        ("CAR-07", "Schneider National Truckload", "Road", 0.09)
    ]

    shipment_records = []
    shipment_counter = 5001

    for idx, po in df_po.iterrows():
        # Generate shipment for most POs
        if idx >= 140:
            break
        
        ship_id = f"SHP-{shipment_counter}"
        shipment_counter += 1

        po_id = po["purchase_order_id"]
        order_dt = datetime.strptime(po["order_date"], "%Y-%m-%d")
        promised_dt = datetime.strptime(po["promised_delivery_date"], "%Y-%m-%d")

        # Pick carrier
        c = random.choice(carriers)
        car_id, car_name, mode, base_delay_prob = c

        # Transit time based on mode
        transit_days = {
            "Air": random.randint(3, 7),
            "Road": random.randint(2, 6),
            "Rail": random.randint(10, 20),
            "Ocean": random.randint(22, 42)
        }[mode]

        # Ship date shortly after order date
        ship_dt = max(order_dt + timedelta(days=2), promised_dt - timedelta(days=transit_days))
        est_arrival_dt = ship_dt + timedelta(days=transit_days)

        sup_loc = df_suppliers[df_suppliers["supplier_id"] == po["supplier_id"]]["supplier_location"].values[0]
        dest_plant = random.choice(["PL-NORTH (Chicago, USA)", "PL-SOUTH (Atlanta, USA)", "PL-EAST (Rotterdam, EU)"])

        # Shipping cost based on mode and weight/qty
        weight_factor = po["quantity_ordered"] * 0.02
        mode_rate = {"Air": 12.5, "Ocean": 1.8, "Road": 3.2, "Rail": 2.4}[mode]
        shipping_cost = round(max(350.0, weight_factor * mode_rate + random.uniform(100, 300)), 2)

        # Arrival date logic
        today_ref = BASE_DATE + timedelta(days=260)
        if est_arrival_dt < today_ref:
            # Arrived
            is_delayed = random.random() < (base_delay_prob * (2.2 if "Rail" in mode or "Ocean" in mode else 1.0))
            if is_delayed or po["purchase_order_status"] in ["Delivered Late", "Delayed Open"]:
                delay = random.randint(4, 18)
                act_arr = est_arrival_dt + timedelta(days=delay)
                s_status = "Delivered Late"
            else:
                act_arr = est_arrival_dt + timedelta(days=random.randint(-2, 0))
                s_status = "Delivered On-Time"
            act_str = act_arr.strftime("%Y-%m-%d")
        else:
            # In transit
            act_str = ""
            if est_arrival_dt < today_ref:
                s_status = "In-Transit Delayed"
            else:
                s_status = "In-Transit On-Schedule"

        shipment_records.append({
            "shipment_id": ship_id,
            "purchase_order_id": po_id,
            "carrier_id": car_id,
            "transport_mode": mode,
            "origin": sup_loc,
            "destination": dest_plant,
            "shipment_date": ship_dt.strftime("%Y-%m-%d"),
            "estimated_arrival_date": est_arrival_dt.strftime("%Y-%m-%d"),
            "actual_arrival_date": act_str,
            "shipment_status": s_status,
            "shipping_cost": shipping_cost
        })

    df_trans = pd.DataFrame(shipment_records)
    df_trans.to_csv(os.path.join(output_dir, "transportation.csv"), index=False)

    # ---------------------------------------------------------
    # 7. PRODUCTION ORDERS (45 Orders across 3 Plants)
    # ---------------------------------------------------------
    prod_records = []
    prod_counter = 8001

    for i in range(45):
        pr_id = f"PRD-{prod_counter}"
        prod_counter += 1

        p_id = random.choice(products)
        plant = random.choice(plants)
        qty_plan = random.choice([50, 100, 150, 200, 300, 500])

        # Scheduling window
        start_day = random.randint(100, 310)
        plan_start_dt = BASE_DATE + timedelta(days=start_day)
        duration_days = random.randint(7, 21)
        plan_comp_dt = plan_start_dt + timedelta(days=duration_days)

        today_ref = BASE_DATE + timedelta(days=260)

        # Get critical material required for this product
        bom_for_p = df_bom[df_bom["product_id"] == p_id]
        crit_mats = bom_for_p[bom_for_p["material_criticality"].isin(["Critical", "High"])]
        chosen_mat = crit_mats.iloc[0]["material_id"] if len(crit_mats) > 0 else bom_for_p.iloc[0]["material_id"]
        qty_per_unit = bom_for_p[bom_for_p["material_id"] == chosen_mat]["quantity_required_per_unit"].values[0]
        mat_qty_req = int(round(qty_plan * qty_per_unit))

        if plan_comp_dt < today_ref:
            # Past order: Completed
            if random.random() < 0.2:
                # Delayed completion
                delay = random.randint(3, 14)
                act_comp_dt = plan_comp_dt + timedelta(days=delay)
                comp_qty = int(round(qty_plan * np.random.uniform(0.85, 1.0)))
                p_status = "Completed with Delay"
            else:
                act_comp_dt = plan_comp_dt
                comp_qty = qty_plan
                p_status = "Completed On-Schedule"
            act_comp_str = act_comp_dt.strftime("%Y-%m-%d")
        elif plan_start_dt <= today_ref <= plan_comp_dt:
            # In progress
            act_comp_str = ""
            comp_qty = int(round(qty_plan * 0.45))
            # Check if chosen material has severe shortage
            if chosen_mat in ["MAT-101", "MAT-111", "MAT-119", "MAT-124", "MAT-135"]:
                p_status = "Halted - Material Shortage"
            else:
                p_status = "In Progress"
        else:
            # Future planned order
            act_comp_str = ""
            comp_qty = 0
            if chosen_mat in ["MAT-101", "MAT-111", "MAT-119", "MAT-124", "MAT-135"]:
                p_status = "At Risk - Material Shortage"
            else:
                p_status = "Scheduled Confirmed"

        prod_records.append({
            "production_order_id": pr_id,
            "product_id": p_id,
            "plant_id": plant,
            "planned_start_date": plan_start_dt.strftime("%Y-%m-%d"),
            "planned_completion_date": plan_comp_dt.strftime("%Y-%m-%d"),
            "actual_completion_date": act_comp_str,
            "planned_quantity": qty_plan,
            "completed_quantity": comp_qty,
            "production_status": p_status,
            "material_id": chosen_mat,
            "material_quantity_required": mat_qty_req
        })

    df_production = pd.DataFrame(prod_records)
    df_production.to_csv(os.path.join(output_dir, "production.csv"), index=False)

    # ---------------------------------------------------------
    # 8. HISTORICAL DEMAND (Weekly Demand over 36 weeks for Products & Materials)
    # ---------------------------------------------------------
    demand_records = []
    # 36 weekly intervals
    for w in range(36):
        f_dt = BASE_DATE + timedelta(weeks=w)
        f_str = f_dt.strftime("%Y-%m-%d")

        for p_id in products:
            base_p_demand = {"PROD-01": 180, "PROD-02": 120, "PROD-03": 210, "PROD-04": 95,
                             "PROD-05": 70, "PROD-06": 55, "PROD-07": 85, "PROD-08": 140}[p_id]
            
            # Add seasonality, trend, and occasional demand spike (weeks 22-26)
            trend = 1.0 + (w * 0.008)
            spike = 1.45 if (22 <= w <= 26 and p_id in ["PROD-01", "PROD-03", "PROD-06"]) else 1.0
            noise = np.random.normal(1.0, 0.08)
            
            forecast_qty = int(round(base_p_demand * trend))
            actual_qty = int(round(base_p_demand * trend * spike * noise)) if w <= 32 else int(round(forecast_qty * noise))
            variability = round(float(abs(actual_qty - forecast_qty) / max(forecast_qty, 1)), 3)

            # Map to primary critical material
            crit_mats = df_bom[(df_bom["product_id"] == p_id) & (df_bom["material_criticality"] == "Critical")]
            mat_id = crit_mats.iloc[0]["material_id"] if len(crit_mats) > 0 else "MAT-101"

            demand_records.append({
                "product_id": p_id,
                "material_id": mat_id,
                "forecast_date": f_str,
                "forecast_quantity": forecast_qty,
                "actual_demand": actual_qty,
                "demand_variability": variability
            })

    df_demand = pd.DataFrame(demand_records)
    df_demand.to_csv(os.path.join(output_dir, "demand.csv"), index=False)

    print(f"[OK] Successfully generated all 7 synthetic datasets in '{output_dir}/':")
    print(f"  - suppliers.csv: {len(df_suppliers)} rows")
    print(f"  - inventory.csv: {len(df_inventory)} rows")
    print(f"  - purchase_orders.csv: {len(df_po)} rows")
    print(f"  - bill_of_materials.csv: {len(df_bom)} rows")
    print(f"  - production.csv: {len(df_production)} rows")
    print(f"  - transportation.csv: {len(df_trans)} rows")
    print(f"  - demand.csv: {len(df_demand)} rows")

if __name__ == "__main__":
    generate_all_datasets("data")
