import frappe
import os

no_cache = 1

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    paths_to_try = [
        os.path.join(base_dir, "www", "car-dashboard.html"),
        os.path.join(base_dir, "www", "car-dashboard", "index.html"),
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                context.car_page_html = f.read()
            return context
    context.car_page_html = "<h1>Car Dashboard</h1><p>Loading...</p>"
    return context
