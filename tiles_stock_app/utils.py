from functools import wraps
from flask import session, flash, redirect

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

TILE_CATEGORIES = [
    "Bathroom Tiles",
    "Room Tiles",
    "Parking Tiles",
    "Elevation Tiles",
    "Kitchen Tiles"
]

SANITARY_CATEGORIES = [
    "Commode (Western)",
    "Indian Seat",
    "Sink / Wash Basin",
    "Urinal",
    "Bathroom Accessories"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first")
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        if session.get('role') != "admin":
            flash("Admin access required")
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return wrapper
