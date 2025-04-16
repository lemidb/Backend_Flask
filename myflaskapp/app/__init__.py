from flask import Flask
from app.config import Config
from app.extensions import db, jwt
from app.routes import auth_bp, item_bp, product_bp

def create_app():
    """Application factory pattern for initializing the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    initialize_extensions(app)

    # Register Blueprints (Routes)
    register_blueprints(app)

    return app

def initialize_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    jwt.init_app(app)

    # Ensure tables are created (only for SQLite or initial dev setup)
    with app.app_context():
        db.create_all()

def register_blueprints(app):
    """Register all application blueprints."""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(item_bp, url_prefix='/api/data')
    app.register_blueprint(product_bp, url_prefix='/api/productdata')
