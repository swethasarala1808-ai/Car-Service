import frappe
import os

no_cache = 1

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    app_path = frappe.get_app_path("car_app")
    paths = [
        os.path.join(app_path, "www", "car-dashboard.html"),
        os.path.join(app_path, "www", "car-dashboard", "index.html"),
        os.path.join(app_path, "templates", "pages", "car-dashboard.html"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                context.car_page_html = f.read()
            return context
    context.car_page_html = "<h1>Car Dashboard</h1>"
    return context
