from flask import Blueprint, render_template, request, redirect, flash, url_for, current_app, make_response
from werkzeug.utils import secure_filename
import os, time, traceback, io
from ..models import Tile, SanitaryProduct, OnlineOrder, SanitaryOrder, Bill
from ..extensions import db
from ..utils import login_required, admin_required, allowed_file, TILE_CATEGORIES, SANITARY_CATEGORIES
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/")
def index():
    return redirect('/dashboard')

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    tiles = Tile.query.all()
    sanitary_products = SanitaryProduct.query.all()
    return render_template("dashboard.html", tiles=tiles, categories=TILE_CATEGORIES,
                           sanitary_products=sanitary_products, sanitary_categories=SANITARY_CATEGORIES)

@admin_bp.route("/add_tile", methods=["GET", "POST"])
@admin_required
def add_tile():
    if request.method == "POST":
        image_filename = None
        file = request.files.get('tile_image')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        tile = Tile(
            brand=request.form['brand'],
            category=request.form.get('category'),
            size=request.form['size'],
            buy_price=float(request.form.get('buy_price') or 0),
            price=float(request.form['price']),
            quantity=int(request.form['quantity']),
            image_filename=image_filename
        )
        db.session.add(tile)
        db.session.commit()
        flash("Tile added successfully")
        return redirect("/dashboard")
    return render_template("add_tile.html", categories=TILE_CATEGORIES)

@admin_bp.route("/edit_tile/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_tile(id):
    try:
        tile = Tile.query.get_or_404(id)
        if request.method == "POST":
            tile.brand = request.form['brand']
            tile.category = request.form.get('category')
            tile.size = request.form['size']
            tile.buy_price = float(request.form.get('buy_price') or 0)
            tile.price = float(request.form['price'])
            tile.quantity = int(request.form['quantity'])

            file = request.files.get('tile_image')
            if file and file.filename and allowed_file(file.filename):
                if tile.image_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], tile.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                tile.image_filename = filename

            if request.form.get('remove_image') == '1':
                if tile.image_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], tile.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                tile.image_filename = None

            db.session.commit()
            flash("Tile updated successfully")
            return redirect("/dashboard")
        return render_template("add_tile.html", tile=tile, categories=TILE_CATEGORIES)
    except Exception as e:
        flash(f"System Error: {str(e)}")
        return redirect("/dashboard")

@admin_bp.route("/delete_tile/<int:id>")
@admin_required
def delete_tile(id):
    tile = Tile.query.get_or_404(id)
    db.session.delete(tile)
    db.session.commit()
    flash("Tile deleted successfully")
    return redirect("/dashboard")

@admin_bp.route("/add_sanitary", methods=["GET", "POST"])
@admin_required
def add_sanitary():
    if request.method == "POST":
        image_filename = None
        file = request.files.get('product_image')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        product = SanitaryProduct(
            name=request.form['name'],
            category=request.form['category'],
            brand=request.form.get('brand'),
            size=request.form.get('size'),
            price=float(request.form['price']),
            quantity=int(request.form['quantity']),
            description=request.form.get('description'),
            image_filename=image_filename
        )
        db.session.add(product)
        db.session.commit()
        flash("Sanitary product added successfully")
        return redirect("/dashboard")
    return render_template("add_sanitary.html", categories=SANITARY_CATEGORIES)

@admin_bp.route("/edit_sanitary/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_sanitary(id):
    try:
        product = SanitaryProduct.query.get_or_404(id)
        if request.method == "POST":
            product.name = request.form['name']
            product.category = request.form['category']
            product.brand = request.form.get('brand')
            product.size = request.form.get('size')
            product.price = float(request.form['price'])
            product.quantity = int(request.form['quantity'])
            product.description = request.form.get('description')

            file = request.files.get('product_image')
            if file and file.filename and allowed_file(file.filename):
                if product.image_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                filename = secure_filename(file.filename)
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                product.image_filename = filename

            if request.form.get('remove_image') == '1':
                if product.image_filename:
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                product.image_filename = None

            db.session.commit()
            flash("Sanitary product updated successfully")
            return redirect("/dashboard")
        return render_template("add_sanitary.html", product=product, categories=SANITARY_CATEGORIES)
    except Exception as e:
        flash(f"System Error: {str(e)}")
        return redirect("/dashboard")

@admin_bp.route("/delete_sanitary/<int:id>")
@admin_required
def delete_sanitary(id):
    product = SanitaryProduct.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Sanitary product deleted successfully")
    return redirect("/dashboard")

@admin_bp.route("/admin/orders")
@admin_required
def admin_orders():
    status_filter = request.args.get('status', '')
    orders = OnlineOrder.query
    if status_filter:
        orders = orders.filter_by(status=status_filter)
    orders = orders.order_by(OnlineOrder.created_at.desc()).all()
    
    sanitary_orders = SanitaryOrder.query
    if status_filter:
        sanitary_orders = sanitary_orders.filter_by(status=status_filter)
    sanitary_orders = sanitary_orders.order_by(SanitaryOrder.created_at.desc()).all()
    
    return render_template("orders.html", orders=orders, sanitary_orders=sanitary_orders, status_filter=status_filter)

@admin_bp.route("/admin/orders/update/<int:order_id>", methods=["POST"])
@admin_required
def update_order_status(order_id):
    order = OnlineOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('confirmed', 'rejected', 'pending'):
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} marked as {new_status}")
    return redirect(url_for('admin.admin_orders'))

@admin_bp.route("/admin/orders/update_sanitary/<int:order_id>", methods=["POST"])
@admin_required
def update_sanitary_order_status(order_id):
    order = SanitaryOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('confirmed', 'rejected', 'pending'):
        order.status = new_status
        db.session.commit()
        flash(f"Sanitary Order #{order.id} marked as {new_status}")
    return redirect(url_for('admin.admin_orders'))

@admin_bp.route("/sales_report")
@admin_required
def sales_report():
    total_sales = db.session.query(func.sum(Bill.total)).scalar() or 0
    total_bills = Bill.query.count()
    return render_template(
        "sales_report.html",
        total_sales=total_sales,
        total_bills=total_bills
    )

@admin_bp.route("/stock_availability_pdf")
@admin_required
def stock_availability_pdf():
    from xhtml2pdf import pisa
    tiles = Tile.query.all()
    html = render_template("stock_availability_pdf.html", tiles=tiles)
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = "attachment; filename=stock_availability.pdf"
    return response

