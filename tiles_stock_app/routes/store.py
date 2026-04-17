from flask import Blueprint, render_template, request, redirect, flash, url_for
from ..models import Tile, SanitaryProduct, OnlineOrder, SanitaryOrder
from ..extensions import db
from ..utils import TILE_CATEGORIES, SANITARY_CATEGORIES

store_bp = Blueprint('store', __name__)

@store_bp.route("/")
def index():
    return redirect(url_for("store.store"))

@store_bp.route("/store")
def store():
    search = request.args.get('search', '').strip()
    size_filter = request.args.get('size', '').strip()
    tiles = Tile.query.filter(Tile.quantity > 0)
    if search:
        tiles = tiles.filter(Tile.brand.ilike(f'%{search}%'))
    if size_filter:
        tiles = tiles.filter(Tile.size == size_filter)
    tiles = tiles.all()
    all_sizes = db.session.query(Tile.size).distinct().all()
    all_sizes = [s[0] for s in all_sizes]
    
    sanitary_products = SanitaryProduct.query.filter(SanitaryProduct.quantity > 0)
    if search:
        sanitary_products = sanitary_products.filter(SanitaryProduct.name.ilike(f'%{search}%') | SanitaryProduct.brand.ilike(f'%{search}%'))
    sanitary_products = sanitary_products.all()
    
    return render_template("store.html", tiles=tiles, all_sizes=all_sizes,
                           search=search, size_filter=size_filter, categories=TILE_CATEGORIES,
                           sanitary_products=sanitary_products, sanitary_categories=SANITARY_CATEGORIES)

@store_bp.route("/store/order/<int:tile_id>", methods=["POST"])
def place_online_order(tile_id):
    tile = Tile.query.get_or_404(tile_id)
    qty = int(request.form.get('quantity', 1))
    if qty < 1 or tile.quantity < qty:
        flash("Requested quantity not available")
        return redirect(url_for('store.store'))
    order = OnlineOrder(
        customer_name=request.form.get('customer_name', '').strip(),
        customer_mobile=request.form.get('customer_mobile', '').strip(),
        customer_email=request.form.get('customer_email', '').strip(),
        customer_address=request.form.get('customer_address', '').strip(),
        tile_id=tile.id,
        quantity=qty,
        total_price=tile.price * qty,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    return render_template("order_success.html", order=order, tile=tile)


@store_bp.route("/store/order_sanitary/<int:id>", methods=["POST"])
def place_sanitary_order(id):
    product = SanitaryProduct.query.get_or_404(id)
    qty = int(request.form.get('quantity', 1))
    if qty < 1 or product.quantity < qty:
        flash("Requested quantity not available")
        return redirect(url_for('store.store'))
    order = SanitaryOrder(
        customer_name=request.form.get('customer_name', '').strip(),
        customer_mobile=request.form.get('customer_mobile', '').strip(),
        customer_email=request.form.get('customer_email', '').strip(),
        customer_address=request.form.get('customer_address', '').strip(),
        sanitary_id=product.id,
        quantity=qty,
        total_price=product.price * qty,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    return render_template("order_success.html", order=order, product=product)

@store_bp.route("/contact")
def contact():
    return render_template("contact.html")
