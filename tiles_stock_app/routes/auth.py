from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..extensions import db
from ..utils import admin_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect('/dashboard')

    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            if not user.is_active:
                flash("Account deactivated")
                return render_template("login.html")

            session['user_id'] = user.id
            session['role'] = user.role
            session['user'] = user.username
            return redirect('/dashboard')

        flash("Invalid credentials")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/store")

@auth_bp.route("/user_management")
@admin_required
def user_management():
    users = User.query.all()
    return render_template("user_management.html", users=users)

@auth_bp.route("/create_user", methods=["GET", "POST"])
@admin_required
def create_user():
    if request.method == "POST":
        username = request.form['username']
        email = request.form.get('email')
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash("Passwords do not match")
            return render_template("add_user.html")
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return render_template("add_user.html")

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        flash("User created successfully")
        return redirect(url_for("auth.user_management"))

    return render_template("add_user.html")

@auth_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.email = request.form.get('email')
        user.role = request.form['role']
        new_password = request.form.get('new_password')
        if new_password:
            user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("User updated successfully")
        return redirect(url_for("auth.user_management"))
    return render_template("edit_user.html", user=user)

@auth_bp.route("/toggle_user_status/<int:user_id>", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    if user_id == session.get('user_id'):
        flash("Cannot deactivate yourself")
        return redirect(url_for("auth.user_management"))
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'deactivated'} successfully")
    return redirect(url_for("auth.user_management"))

@auth_bp.route("/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash("Cannot delete yourself")
        return redirect(url_for("auth.user_management"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for("auth.user_management"))
