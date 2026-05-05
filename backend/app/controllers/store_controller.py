from flask import render_template, request, redirect, flash, url_for
from ..models import Tile, SanitaryProduct, OtherProduct, OnlineOrder, SanitaryOrder, OtherOrder
from ..extensions import db
from ..utils import TILE_CATEGORIES, SANITARY_CATEGORIES, OTHER_CATEGORIES

def get_store_data():
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
    
    other_products = OtherProduct.query.filter(OtherProduct.quantity > 0)
    if search:
        other_products = other_products.filter(OtherProduct.name.ilike(f'%{search}%') | OtherProduct.brand.ilike(f'%{search}%'))
    other_products = other_products.all()
    
    return render_template("store.html", tiles=tiles, all_sizes=all_sizes,
                           search=search, size_filter=size_filter, categories=TILE_CATEGORIES,
                           sanitary_products=sanitary_products, sanitary_categories=SANITARY_CATEGORIES,
                           other_products=other_products, other_categories=OTHER_CATEGORIES)

def place_tile_order_logic(tile_id):
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

def place_sanitary_order_logic(id):
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

def place_other_order_logic(id):
    product = OtherProduct.query.get_or_404(id)
    qty = int(request.form.get('quantity', 1))
    if qty < 1 or product.quantity < qty:
        flash("Requested quantity not available")
        return redirect(url_for('store.store'))
    order = OtherOrder(
        customer_name=request.form.get('customer_name', '').strip(),
        customer_mobile=request.form.get('customer_mobile', '').strip(),
        customer_email=request.form.get('customer_email', '').strip(),
        customer_address=request.form.get('customer_address', '').strip(),
        other_id=product.id,
        quantity=qty,
        total_price=product.price * qty,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()
    return render_template("order_success.html", order=order, product=product)

def get_contact_page():
    return render_template("contact.html")
