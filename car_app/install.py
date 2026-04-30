import frappe

def after_install():
    create_settings()
    create_services()
    create_mechanics()
    create_spare_parts()

def create_settings():
    if not frappe.db.exists("Car Settings", "Car Settings"):
        doc = frappe.get_doc({
            "doctype": "Car Settings",
            "garage_name": "AutoCare Pro",
            "tagline": "Your Trusted Car Service Partner",
            "phone": "+91 9876543210",
            "email": "autocare@example.com",
            "address": "123 Main Road, Chennai, Tamil Nadu",
            "upi_id": "autocare@upi",
            "gst_number": "29XXXXX",
            "google_rating": 4.8,
            "working_hours": "Mon-Sat 8AM-7PM",
            "total_vehicles_served": 5000,
            "experience_years": 10
        })
        doc.insert(ignore_permissions=True)

def create_services():
    services = [
        ("Oil Change", "Oil Change", 800, 30),
        ("AC Service", "AC Service", 2500, 120),
        ("Full Brake Service", "Brake Service", 3500, 90),
        ("Engine Tune-up", "Engine Repair", 2000, 60),
        ("Wheel Alignment", "General Service", 600, 30),
        ("Tyre Rotation", "Tyre", 400, 20),
        ("Battery Check", "Electrical", 300, 15),
        ("Coolant Flush", "General Service", 800, 30),
        ("Transmission Service", "Engine Repair", 3000, 120),
        ("Full Body Wash", "Body Work", 500, 30),
        ("Interior Cleaning", "Body Work", 800, 60),
        ("Windshield Repair", "Body Work", 1500, 45),
        ("Electrical Diagnosis", "Electrical", 1000, 60),
        ("Clutch Repair", "Engine Repair", 4500, 180),
        ("General Service", "General Service", 2500, 90),
    ]
    for name, cat, price, dur in services:
        if not frappe.db.exists("Car Service", name):
            frappe.get_doc({
                "doctype": "Car Service",
                "service_name": name,
                "category": cat,
                "price": price,
                "duration_minutes": dur,
                "is_active": 1
            }).insert(ignore_permissions=True)

def create_mechanics():
    mechanics = [
        ("Rajan Kumar", "Engine", 8, "9876500001"),
        ("Selvam M", "Electrical", 6, "9876500002"),
        ("Priya S", "AC", 5, "9876500003"),
        ("Arun T", "General", 4, "9876500004"),
    ]
    for name, spec, exp, phone in mechanics:
        if not frappe.db.exists("Car Mechanic", name):
            frappe.get_doc({
                "doctype": "Car Mechanic",
                "mechanic_name": name,
                "specialization": spec,
                "experience_years": exp,
                "phone": phone,
                "shift": "Both",
                "is_active": 1,
                "total_jobs": 0
            }).insert(ignore_permissions=True)

def create_spare_parts():
    parts = [
        ("Engine Oil", "Oil", "Castrol", 450, 20, 5, "Litre"),
        ("Oil Filter", "Filter", "Bosch", 120, 15, 5, "Nos"),
        ("Air Filter", "Filter", "K&N", 350, 10, 3, "Nos"),
        ("Brake Pads", "Brake", "Brembo", 800, 8, 3, "Set"),
        ("Coolant", "Engine", "Prestone", 250, 12, 4, "Litre"),
        ("Spark Plugs", "Engine", "NGK", 180, 20, 5, "Nos"),
        ("Wiper Blades", "Body", "Bosch", 300, 10, 3, "Pair"),
        ("Battery", "Electrical", "Amaron", 3500, 5, 2, "Nos"),
        ("AC Filter", "AC", "Mahle", 400, 8, 3, "Nos"),
        ("Brake Fluid", "Brake", "Castrol", 200, 10, 3, "Litre"),
    ]
    for name, cat, brand, price, stock, reorder, unit in parts:
        if not frappe.db.exists("Car Spare Part", name):
            frappe.get_doc({
                "doctype": "Car Spare Part",
                "part_name": name,
                "category": cat,
                "brand": brand,
                "price": price,
                "stock_qty": stock,
                "reorder_level": reorder,
                "unit": unit,
                "is_active": 1
            }).insert(ignore_permissions=True)
    frappe.db.commit()
