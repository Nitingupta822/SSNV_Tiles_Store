from flask import Blueprint, redirect, url_for
from ..utils import login_required, admin_required
from ..controllers import admin_controller

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/")
def index():
    return redirect(url_for('store.store'))

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    return admin_controller.get_dashboard_data()

@admin_bp.route("/add_tile", methods=["GET", "POST"])
@admin_required
def add_tile():
    return admin_controller.add_tile_logic()

@admin_bp.route("/edit_tile/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_tile(id):
    return admin_controller.edit_tile_logic(id)

@admin_bp.route("/delete_tile/<int:id>")
@admin_required
def delete_tile(id):
    return admin_controller.delete_tile_logic(id)

@admin_bp.route("/add_sanitary", methods=["GET", "POST"])
@admin_required
def add_sanitary():
    return admin_controller.add_sanitary_logic()

@admin_bp.route("/edit_sanitary/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_sanitary(id):
    return admin_controller.edit_sanitary_logic(id)

@admin_bp.route("/delete_sanitary/<int:id>")
@admin_required
def delete_sanitary(id):
    return admin_controller.delete_sanitary_logic(id)

@admin_bp.route("/admin/orders")
@admin_required
def admin_orders():
    return admin_controller.get_orders_logic()

@admin_bp.route("/admin/orders/update/<int:order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id):
    return admin_controller.update_order_status_logic(order_id)

@admin_bp.route("/admin/orders/update_sanitary/<int:order_id>", methods=["POST"])
@admin_required
def update_sanitary_order_status(order_id):
    return admin_controller.update_sanitary_order_status_logic(order_id)

@admin_bp.route("/admin/orders/update_other/<int:order_id>", methods=["POST"])
@admin_required
def update_other_order_status(order_id):
    return admin_controller.update_other_order_status_logic(order_id)

@admin_bp.route("/add_other", methods=["GET", "POST"])
@admin_required
def add_other():
    return admin_controller.add_other_logic()

@admin_bp.route("/edit_other/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_other(id):
    return admin_controller.edit_other_logic(id)

@admin_bp.route("/delete_other/<int:id>")
@admin_required
def delete_other(id):
    return admin_controller.delete_other_logic(id)

@admin_bp.route("/sales_report")
@admin_required
def sales_report():
    return admin_controller.get_sales_report_logic()

@admin_bp.route("/stock_availability_pdf")
@admin_required
def stock_availability_pdf():
    return admin_controller.generate_stock_pdf_logic()
