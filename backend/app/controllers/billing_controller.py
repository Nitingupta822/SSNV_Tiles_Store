from flask import render_template, request, redirect, flash, url_for, make_response, current_app
import io
import os
from ..models import Tile, SanitaryProduct, OtherProduct, Bill, BillItem
from ..extensions import db

def create_bill_logic():
    try:
        tiles = Tile.query.all()
        sanitary_products = SanitaryProduct.query.all()
        other_products = OtherProduct.query.all()

        if request.method == "POST":
            bill = Bill(
                customer_name=request.form.get("customer_name"),
                customer_mobile=request.form.get("customer_mobile"),
                total=0,
                gst=float(request.form.get("gst") or 0),
                discount=float(request.form.get("discount") or 0)
            )
            db.session.add(bill)
            db.session.commit()

            subtotal = 0

            # Process Tiles
            for tile in tiles:
                qty_str = request.form.get(f"qty_{tile.id}", "0")
                qty = int(qty_str) if qty_str.isdigit() else 0
                
                if qty > 0 and tile.quantity >= qty:
                    tile.quantity -= qty
                    item_total = tile.price * qty
                    subtotal += item_total

                    item = BillItem(
                        bill_id=bill.id,
                        tile_name=tile.brand,
                        size=tile.size,
                        price=tile.price,
                        quantity=qty,
                        total=item_total
                    )
                    db.session.add(item)
                    
            # Process Sanitary Products
            for product in sanitary_products:
                qty_str = request.form.get(f"qty_sanitary_{product.id}", "0")
                qty = int(qty_str) if qty_str.isdigit() else 0
                
                if qty > 0 and product.quantity >= qty:
                    product.quantity -= qty
                    item_total = product.price * qty
                    subtotal += item_total

                    item = BillItem(
                        bill_id=bill.id,
                        tile_name=product.name,
                        size=product.brand, # Store brand here for sanitary products
                        price=product.price,
                        quantity=qty,
                        total=item_total
                    )
                    db.session.add(item)
                    
            # Process Other Products
            for product in other_products:
                qty_str = request.form.get(f"qty_other_{product.id}", "0")
                qty = int(qty_str) if qty_str.isdigit() else 0
                
                if qty > 0 and product.quantity >= qty:
                    product.quantity -= qty
                    item_total = product.price * qty
                    subtotal += item_total

                    item = BillItem(
                        bill_id=bill.id,
                        tile_name=product.name,
                        size=product.category, # Store category as size for misc items
                        price=product.price,
                        quantity=qty,
                        total=item_total
                    )
                    db.session.add(item)

            bill.total = subtotal + (subtotal * bill.gst / 100) - bill.discount
            db.session.commit()

            return redirect(url_for("billing.invoice", bill_id=bill.id))

        return render_template("billing.html", tiles=tiles, sanitary_products=sanitary_products, other_products=other_products)
    except Exception as e:
        db.session.rollback()
        flash(f"Error in billing: {str(e)}")
        return redirect(url_for("admin.dashboard"))

def get_sales_history_logic():
    bills = Bill.query.order_by(Bill.date.desc()).all()
    return render_template("history.html", bills=bills)

def delete_bill_logic(id):
    bill = Bill.query.get_or_404(id)
    db.session.delete(bill)
    db.session.commit()
    flash("Invoice deleted successfully")
    return redirect(url_for('billing.sales_history'))

def edit_bill_logic(id):
    bill = Bill.query.get_or_404(id)
    if request.method == "POST":
        try:
            bill.customer_name = request.form.get('customer_name')
            bill.customer_mobile = request.form.get('customer_mobile')
            bill.gst = float(request.form.get('gst') or 0)
            bill.discount = float(request.form.get('discount') or 0)
            
            items = BillItem.query.filter_by(bill_id=bill.id).all()
            subtotal = sum(item.total for item in items)
            bill.total = subtotal + (subtotal * bill.gst / 100) - bill.discount
            
            db.session.commit()
            flash("Invoice updated successfully")
            return redirect(url_for('billing.sales_history'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating invoice: {str(e)}")
            return render_template("edit_bill.html", bill=bill)
    return render_template("edit_bill.html", bill=bill)

def clear_history_logic():
    try:
        BillItem.query.delete()
        Bill.query.delete()
        db.session.commit()
        flash("All sales history cleared")
    except Exception as e:
        db.session.rollback()
        flash(f"Error clearing history: {str(e)}")
    return redirect(url_for('billing.sales_history'))

def get_invoice_logic(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill_id).all()

    msg = f"🏬 *SSNV Store*\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"Dear {bill.customer_name or 'Customer'},\n"
    msg += f"Thank you for shopping with us! 🙏\n\n"
    msg += f"🧾 *Invoice #{bill.id}*\n"
    msg += f"📅 Date: {bill.date.strftime('%d %b %Y') if bill.date else 'N/A'}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"🛒 *Items Purchased:*\n"

    subtotal = 0
    for i, item in enumerate(items, 1):
        subtotal += item.total
        msg += f"{i}. {item.tile_name} ({item.size})\n"
        msg += f"   Qty: {item.quantity} × ₹{item.price:.2f} = ₹{item.total:.2f}\n"

    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"Subtotal:  ₹{subtotal:.2f}\n"
    if bill.gst:
        msg += f"GST ({bill.gst}%): ₹{subtotal * bill.gst / 100:.2f}\n"
    if bill.discount:
        msg += f"Discount:  -₹{bill.discount:.2f}\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n"
    msg += f"💰 *Grand Total: ₹{bill.total:.2f}*\n"
    msg += f"━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"Have a great day! 😊\n"
    msg += f"— SSNV Store Team"

    return render_template("invoice.html", bill=bill, items=items, whatsapp_message=msg)

def generate_invoice_pdf_logic(bill_id):
    from xhtml2pdf import pisa
    bill = Bill.query.get_or_404(bill_id)
    items = BillItem.query.filter_by(bill_id=bill_id).all()
    
    # Calculate absolute paths for images (required by xhtml2pdf)
    logo_path = os.path.abspath(os.path.join(current_app.static_folder, 'images', 'ssnv_logo.png'))
    signature_path = os.path.abspath(os.path.join(current_app.static_folder, 'images', 'signature.png'))
    
    html = render_template("invoice_pdf.html", 
                           bill=bill, 
                           items=items, 
                           logo_path=logo_path, 
                           signature_path=signature_path)
    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result)
    response = make_response(result.getvalue())
    response.headers['Content-Type'] = "application/pdf"
    response.headers['Content-Disposition'] = f"attachment; filename=invoice_{bill.id}.pdf"
    return response
