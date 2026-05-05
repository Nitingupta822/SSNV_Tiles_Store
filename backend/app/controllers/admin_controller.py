import os, time, io
from flask import render_template, request, redirect, flash, current_app, make_response, url_for
from ..models import Tile, SanitaryProduct, OtherProduct, OnlineOrder, SanitaryOrder, OtherOrder, Bill
from ..extensions import db
from ..utils import allowed_file, TILE_CATEGORIES, SANITARY_CATEGORIES, OTHER_CATEGORIES
from sqlalchemy import func
from werkzeug.utils import secure_filename

def get_dashboard_data():
    tiles = Tile.query.all()
    sanitary_products = SanitaryProduct.query.all()
    other_products = OtherProduct.query.all()
    return render_template("dashboard.html", 
                           tiles=tiles, 
                           categories=TILE_CATEGORIES,
                           sanitary_products=sanitary_products, 
                           sanitary_categories=SANITARY_CATEGORIES,
                           other_products=other_products,
                           other_categories=OTHER_CATEGORIES)

def add_tile_logic():
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
        return redirect(url_for('admin.dashboard'))
    return render_template("add_tile.html", categories=TILE_CATEGORIES)

def edit_tile_logic(id):
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
            return redirect(url_for('admin.dashboard'))
        return render_template("add_tile.html", tile=tile, categories=TILE_CATEGORIES)
    except Exception as e:
        flash(f"System Error: {str(e)}")
        return redirect(url_for('admin.dashboard'))

def delete_tile_logic(id):
    tile = Tile.query.get_or_404(id)
    db.session.delete(tile)
    db.session.commit()
    flash("Tile deleted successfully")
    return redirect(url_for('admin.dashboard'))

def add_sanitary_logic():
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
        return redirect(url_for('admin.dashboard'))
    return render_template("add_sanitary.html", categories=SANITARY_CATEGORIES)

def edit_sanitary_logic(id):
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
            return redirect(url_for('admin.dashboard'))
        return render_template("add_sanitary.html", product=product, categories=SANITARY_CATEGORIES)
    except Exception as e:
        flash(f"System Error: {str(e)}")
        return redirect(url_for('admin.dashboard'))

def delete_sanitary_logic(id):
    product = SanitaryProduct.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Sanitary product deleted successfully")
    return redirect(url_for('admin.dashboard'))

def get_orders_logic():
    status_filter = request.args.get('status', '')
    orders = OnlineOrder.query
    if status_filter:
        orders = orders.filter_by(status=status_filter)
    orders = orders.order_by(OnlineOrder.created_at.desc()).all()
    
    sanitary_orders = SanitaryOrder.query
    if status_filter:
        sanitary_orders = sanitary_orders.filter_by(status=status_filter)
    sanitary_orders = sanitary_orders.order_by(SanitaryOrder.created_at.desc()).all()
    
    other_orders = OtherOrder.query
    if status_filter:
        other_orders = other_orders.filter_by(status=status_filter)
    other_orders = other_orders.order_by(OtherOrder.created_at.desc()).all()
    
    return render_template("orders.html", 
                           orders=orders, 
                           sanitary_orders=sanitary_orders, 
                           other_orders=other_orders,
                           status_filter=status_filter)

def update_order_status_logic(order_id):
    from flask import url_for
    order = OnlineOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('confirmed', 'rejected', 'pending'):
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} marked as {new_status}")
    return redirect(url_for('admin.admin_orders'))

def update_sanitary_order_status_logic(order_id):
    from flask import url_for
    order = SanitaryOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('confirmed', 'rejected', 'pending'):
        order.status = new_status
        db.session.commit()
        flash(f"Sanitary Order #{order.id} marked as {new_status}")
    return redirect(url_for('admin.admin_orders'))

def get_sales_report_logic():
    total_sales = db.session.query(func.sum(Bill.total)).scalar() or 0
    total_bills = Bill.query.count()
    return render_template(
        "sales_report.html",
        total_sales=total_sales,
        total_bills=total_bills
    )

def generate_stock_pdf_logic():
    from xhtml2pdf import pisa
    tiles = Tile.query.all()
    html = render_template("stock_availability_pdf.html", tiles=tiles)
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = "attachment; filename=stock_availability.pdf"
    return response

def update_other_order_status_logic(order_id):
    order = OtherOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ('confirmed', 'rejected', 'pending'):
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.id} marked as {new_status}")
    return redirect(url_for('admin.admin_orders'))

def add_other_logic():
    if request.method == "POST":
        image_filename = None
        file = request.files.get('product_image')
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        product = OtherProduct(
            name=request.form['name'],
            category=request.form['category'],
            brand=request.form.get('brand'),
            specifications=request.form.get('specifications'),
            buy_price=float(request.form.get('buy_price') or 0),
            price=float(request.form['price']),
            quantity=int(request.form['quantity']),
            description=request.form.get('description'),
            image_filename=image_filename
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully")
        return redirect(url_for('admin.dashboard'))
    return render_template("add_other.html", categories=OTHER_CATEGORIES)

def edit_other_logic(id):
    try:
        product = OtherProduct.query.get_or_404(id)
        if request.method == "POST":
            product.name = request.form['name']
            product.category = request.form['category']
            product.brand = request.form.get('brand')
            product.specifications = request.form.get('specifications')
            product.buy_price = float(request.form.get('buy_price') or 0)
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
            flash("Product updated successfully")
            return redirect(url_for('admin.dashboard'))
        return render_template("add_other.html", product=product, categories=OTHER_CATEGORIES)
    except Exception as e:
        flash(f"System Error: {str(e)}")
        return redirect(url_for('admin.dashboard'))

def delete_other_logic(id):
    product = OtherProduct.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully")
    return redirect(url_for('admin.dashboard'))
