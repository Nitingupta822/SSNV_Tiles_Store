from flask import Blueprint
from ..utils import login_required, admin_required
from ..controllers import billing_controller

billing_bp = Blueprint('billing', __name__)

@billing_bp.route("/billing", methods=["GET", "POST"])
@login_required
def create_bill():
    return billing_controller.create_bill_logic()

@billing_bp.route("/sales_history")
@login_required
def sales_history():
    return billing_controller.get_sales_history_logic()

@billing_bp.route("/delete_bill/<int:id>")
@admin_required
def delete_bill(id):
    return billing_controller.delete_bill_logic(id)

@billing_bp.route("/edit_bill/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_bill(id):
    return billing_controller.edit_bill_logic(id)

@billing_bp.route("/clear_history", methods=["POST"])
@admin_required
def clear_history():
    return billing_controller.clear_history_logic()

@billing_bp.route("/invoice/<int:bill_id>")
@login_required
def invoice(bill_id):
    return billing_controller.get_invoice_logic(bill_id)

@billing_bp.route("/invoice_pdf/<int:bill_id>")
@login_required
def invoice_pdf(bill_id):
    return billing_controller.generate_invoice_pdf_logic(bill_id)
