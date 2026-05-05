from flask import Blueprint, redirect, url_for
from ..controllers import store_controller

store_bp = Blueprint('store', __name__)

@store_bp.route("/")
@store_bp.route("/store")
def store():
    return store_controller.get_store_data()

@store_bp.route("/store/order/<int:tile_id>", methods=["POST"])
def place_online_order(tile_id):
    return store_controller.place_tile_order_logic(tile_id)

@store_bp.route("/store/order_sanitary/<int:id>", methods=["POST"])
def place_sanitary_order(id):
    return store_controller.place_sanitary_order_logic(id)

@store_bp.route("/store/order_other/<int:id>", methods=["POST"])
def place_other_order(id):
    return store_controller.place_other_order_logic(id)

@store_bp.route("/contact")
def contact():
    return store_controller.get_contact_page()
