import frappe
import os

no_cache = 1

def get_context(context):
    context.no_cache = 1
    context.show_sidebar = False
    # Try multiple paths to find the HTML file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # car_app/
    paths_to_try = [
        os.path.join(base_dir, "www", "car.html"),
        os.path.join(base_dir, "www", "car", "index.html"),
        os.path.join(os.path.dirname(__file__), "_car_content.html"),
    ]
    for p in paths_to_try:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                context.car_page_html = f.read()
            return context
    context.car_page_html = "<h1>Car Service Center</h1><p>Page loading...</p>"
    return context
