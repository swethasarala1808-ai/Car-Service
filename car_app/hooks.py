app_name = "car_app"
app_title = "Car Service Center"
app_publisher = "Swetha Sarala"
app_description = "Car Service Center Management"
app_email = "swethasarala1808@gmail.com"
app_license = "MIT"
app_version = "1.0.0"

after_install = "car_app.install.after_install"

website_route_rules = [
    {"from_route": "/car", "to_route": "car"},
    {"from_route": "/car-dashboard", "to_route": "car-dashboard"},
]
