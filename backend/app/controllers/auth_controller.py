from flask import render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from ..extensions import db

def login_logic():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            if not user.is_active:
                flash("Account deactivated")
                return render_template("login.html")

            session['user_id'] = user.id
            session['role'] = user.role
            session['user'] = user.username
            return redirect(url_for('admin.dashboard'))

        flash("Invalid credentials")

    return render_template("login.html")

def logout_logic():
    session.clear()
    return redirect("/store")

def get_users_logic():
    users = User.query.all()
    return render_template("user_management.html", users=users)

def create_user_logic():
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

def edit_user_logic(user_id):
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

def toggle_user_status_logic(user_id):
    if user_id == session.get('user_id'):
        flash("Cannot deactivate yourself")
        return redirect(url_for("auth.user_management"))
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f"User {'activated' if user.is_active else 'deactivated'} successfully")
    return redirect(url_for("auth.user_management"))

def delete_user_logic(user_id):
    if user_id == session.get('user_id'):
        flash("Cannot delete yourself")
        return redirect(url_for("auth.user_management"))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully")
    return redirect(url_for("auth.user_management"))
