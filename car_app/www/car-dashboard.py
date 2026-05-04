import frappe
import os

no_cache = 1

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    html_path = os.path.join(os.path.dirname(__file__), "car-dashboard.html")
    if not os.path.exists(html_path):
        html_path = os.path.join(os.path.dirname(__file__), "car-dashboard", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        context.car_page_html = f.read()
    return context
