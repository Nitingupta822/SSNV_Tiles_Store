import os
import traceback
from flask import Flask, render_template, send_from_directory
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import User

def create_app():
    app = Flask(__name__, 
                template_folder='../../frontend/templates', 
                static_folder='../../frontend/static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.store import store_bp
    from .routes.billing import billing_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(billing_bp)

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.errorhandler(500)
    def handle_500_error(e):
        db.session.rollback()
        err = traceback.format_exc()
        return render_template("500.html", error=err), 500

    @app.errorhandler(404)
    def handle_404_error(e):
        return render_template("404.html", error=e), 404

    @app.route("/health")
    def health():
        return "App is running successfully!"

    with app.app_context():
        # Safety database creation check
        db.create_all()
        try:
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE tile ADD COLUMN image_filename VARCHAR(200)"))
                conn.commit()
        except: pass
        try:
            with db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("ALTER TABLE tile ADD COLUMN category VARCHAR(50)"))
                conn.commit()
        except: pass
        
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                password=generate_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()

    return app
