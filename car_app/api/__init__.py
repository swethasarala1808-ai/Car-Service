import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_services(category=None):
    filters = {"is_active": 1}
    if category and category != "All":
        filters["category"] = category
    return frappe.get_all("Car Service", filters=filters,
        fields=["name", "service_name", "category", "price", "duration_minutes", "description"])

@frappe.whitelist(allow_guest=True)
def get_mechanics():
    return frappe.get_all("Car Mechanic", filters={"is_active": 1},
        fields=["name", "mechanic_name", "specialization", "experience_years", "shift", "total_jobs"])

@frappe.whitelist(allow_guest=True)
def get_settings():
    try:
        return frappe.get_single("Car Settings")
    except Exception:
        return {}

@frappe.whitelist(allow_guest=True)
def get_spare_parts(category=None, low_stock=False):
    filters = {"is_active": 1}
    if category and category != "All":
        filters["category"] = category
    parts = frappe.get_all("Car Spare Part", filters=filters,
        fields=["name", "part_name", "part_number", "category", "brand", "price", "stock_qty", "reorder_level", "unit", "supplier_name", "supplier_phone"])
    if low_stock:
        parts = [p for p in parts if p.get("stock_qty", 0) <= p.get("reorder_level", 5)]
    return parts

@frappe.whitelist(allow_guest=True)
def get_dashboard_stats():
    try:
        from frappe.utils import today, get_first_day, get_last_day
        td = today()
        first = get_first_day(td)
        last = get_last_day(td)
        today_jobs = frappe.db.count("Car Job Card", {"job_date": td})
        completed_today = frappe.db.count("Car Job Card", {"job_date": td, "status": "Delivered"})
        pending_jobs = frappe.db.count("Car Job Card", {"status": ["in", ["Received", "In Progress", "Waiting for Parts"]]})
        total_vehicles = frappe.db.count("Car Vehicle")
        invoices = frappe.get_all("Car Invoice",
            filters={"invoice_date": ["between", [first, last]], "payment_status": "Paid"},
            fields=["grand_total"])
        month_revenue = sum(i.get("grand_total", 0) or 0 for i in invoices)
        try:
            low_stock = frappe.db.sql("SELECT COUNT(*) FROM `tabCar Spare Part` WHERE stock_qty <= reorder_level AND is_active=1")[0][0]
        except Exception:
            low_stock = 0
        return {
            "today_jobs": today_jobs,
            "month_revenue": month_revenue,
            "total_vehicles": total_vehicles,
            "completed_today": completed_today,
            "pending_jobs": pending_jobs,
            "low_stock_count": low_stock
        }
    except Exception as e:
        frappe.log_error(str(e), "Dashboard Stats Error")
        return {"today_jobs":0,"month_revenue":0,"total_vehicles":0,"completed_today":0,"pending_jobs":0,"low_stock_count":0}

@frappe.whitelist(allow_guest=True)
def book_appointment(customer_name, customer_phone, vehicle_number, vehicle_make, service_type, appointment_date, appointment_time, mechanic=None, notes=None):
    doc = frappe.get_doc({
        "doctype": "Car Appointment",
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "vehicle_number": vehicle_number,
        "vehicle_make": vehicle_make,
        "service_type": service_type,
        "mechanic": mechanic or "",
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "status": "Booked",
        "notes": notes or ""
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "status": "Booked"}

@frappe.whitelist(allow_guest=True)
def create_job_card(customer_name, customer_phone, vehicle_number, vehicle_make, vehicle_model, services, mechanic, odometer_in, estimated_amount=0, customer_complaint=None):
    from frappe.utils import today
    doc = frappe.get_doc({
        "doctype": "Car Job Card",
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "vehicle_number": vehicle_number,
        "vehicle_make": vehicle_make,
        "vehicle_model": vehicle_model,
        "services": services,
        "mechanic": mechanic,
        "odometer_in": float(odometer_in or 0),
        "estimated_amount": float(estimated_amount or 0),
        "customer_complaint": customer_complaint or "",
        "job_date": today(),
        "status": "Received"
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "status": "Received"}

@frappe.whitelist(allow_guest=True)
def update_job_status(job_name, new_status):
    doc = frappe.get_doc("Car Job Card", job_name)
    doc.status = new_status
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    # WhatsApp notification
    try:
        settings = frappe.get_single("Car Settings")
        garage = settings.garage_name or "AutoCare Pro"
        phone = settings.phone or ""
        upi_id = settings.upi_id or ""
        cphone = doc.customer_phone or ""
        if cphone and not cphone.startswith("+"):
            cphone = "+91" + cphone.lstrip("0")
        name = doc.customer_name or ""
        vehicle = doc.vehicle_number or ""
        amount = doc.grand_total or doc.estimated_amount or 0
        services = doc.services or ""
        mechanic = doc.mechanic or ""
        next_service = doc.delivery_date or "contact us"
        msg = ""
        if new_status == "Received":
            msg = f"🚗 *Vehicle Received!* Dear *{name}*, your *{vehicle}* has been received at *{garage}*. Job Card: *{job_name}*. We'll send updates as work progresses."
        elif new_status == "In Progress":
            msg = f"🔧 *Work In Progress!* Dear *{name}*, your *{vehicle}* is currently being serviced at *{garage}*. Service: *{services}*. Mechanic: *{mechanic}*"
        elif new_status == "Ready":
            msg = f"✅ *Vehicle Ready!* Dear *{name}*, your *{vehicle}* is ready for pickup at *{garage}*! Amount: *₹{amount}*\n━━━━━━━━━━━━━━━━\n📲 *Pay ₹{amount}:*\nupi://pay?pa={upi_id}&pn={garage}&am={amount}&cu=INR\n━━━━━━━━━━━━━━━━\nOr UPI ID: *{upi_id}*\nFor changes call: *{phone}*"
        elif new_status == "Delivered":
            msg = f"🙏 *Thank You {name}!* Your *{vehicle}* has been delivered. Hope you're satisfied!\n⭐ Rate us on Google!\n📞 Next service: *{next_service}*\nSee you again! 🚗"
        elif new_status == "Cancelled":
            msg = f"❌ *Job Cancelled* Dear *{name}*, job for *{vehicle}* at *{garage}* has been cancelled. Call *{phone}* to rebook."
        if msg and cphone:
            import urllib.parse
            wa_url = f"https://wa.me/{cphone.replace('+','')}?text={urllib.parse.quote(msg)}"
            frappe.log_error(wa_url, "WA")
            return {"status": "updated", "whatsapp_url": wa_url}
    except Exception:
        pass
    return {"status": "updated"}

@frappe.whitelist(allow_guest=True)
def get_vehicle_history(vehicle_number):
    records = frappe.get_all("Car Service Record", filters={"vehicle_number": vehicle_number},
        fields=["name", "service_date", "services_done", "mechanic", "odometer_reading", "total_cost", "next_service_date"],
        order_by="service_date desc")
    jobs = frappe.get_all("Car Job Card", filters={"vehicle_number": vehicle_number},
        fields=["name", "job_date", "services", "mechanic", "status", "grand_total"],
        order_by="job_date desc")
    return {"records": records, "jobs": jobs}

@frappe.whitelist(allow_guest=True)
def open_pos_session(opening_cash=0, opened_by=None):
    try:
        from frappe.utils import today, now_datetime
        existing = frappe.get_all("Car POS Session", filters={"status": "Open"}, limit=1)
        if existing:
            return {"name": existing[0].name, "status": "already_open"}
        now = now_datetime()
        opening_time = now.strftime("%H:%M:%S")
        user = opened_by or "Admin"
        try:
            user = frappe.session.user or "Admin"
        except Exception:
            pass
        doc = frappe.get_doc({
            "doctype": "Car POS Session",
            "session_date": today(),
            "opened_by": user,
            "opening_time": opening_time,
            "opening_cash": float(opening_cash or 0),
            "status": "Open"
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"name": doc.name, "status": "opened"}
    except Exception as e:
        frappe.log_error(str(e), "POS Open Error")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def get_active_pos_session():
    try:
        sessions = frappe.get_all("Car POS Session", filters={"status": "Open"},
            fields=["name", "session_date", "opened_by", "opening_cash", "opening_time"], limit=1)
        return sessions[0] if sessions else None
    except Exception as e:
        frappe.log_error(str(e), "POS Session Error")
        return None

@frappe.whitelist(allow_guest=True)
def close_pos_session(session_name, closing_cash=0, notes=None):
    from frappe.utils import now_datetime
    doc = frappe.get_doc("Car POS Session", session_name)
    invoices = frappe.get_all("Car Invoice", filters={"payment_status": "Paid"}, fields=["grand_total", "payment_method"])
    cash_sales = sum(i.grand_total or 0 for i in invoices if i.payment_method == "Cash")
    upi_sales = sum(i.grand_total or 0 for i in invoices if i.payment_method == "UPI")
    card_sales = sum(i.grand_total or 0 for i in invoices if i.payment_method == "Card")
    total_sales = cash_sales + upi_sales + card_sales
    doc.status = "Closed"
    doc.closing_time = now_datetime().strftime("%H:%M:%S")
    doc.closing_cash = float(closing_cash or 0)
    doc.total_cash_sales = cash_sales
    doc.total_upi_sales = upi_sales
    doc.total_card_sales = card_sales
    doc.total_sales = total_sales
    doc.total_invoices = len(invoices)
    doc.expected_closing = float(doc.opening_cash or 0) + cash_sales
    doc.difference = float(closing_cash or 0) - doc.expected_closing
    doc.notes = notes or ""
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"status": "closed", "total_sales": total_sales}
