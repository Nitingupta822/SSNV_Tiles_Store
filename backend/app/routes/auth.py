from flask import Blueprint
from ..utils import admin_required
from ..controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return auth_controller.login_logic()

@auth_bp.route("/logout")
def logout():
    return auth_controller.logout_logic()

@auth_bp.route("/user_management")
@admin_required
def user_management():
    return auth_controller.get_users_logic()

@auth_bp.route("/create_user", methods=["GET", "POST"])
@admin_required
def create_user():
    return auth_controller.create_user_logic()

@auth_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    return auth_controller.edit_user_logic(user_id)

@auth_bp.route("/toggle_user_status/<int:user_id>", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    return auth_controller.toggle_user_status_logic(user_id)

@auth_bp.route("/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    return auth_controller.delete_user_logic(user_id)
