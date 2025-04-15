from flask import Blueprint
from routes.chat_routes import chat_bp
from routes.inventory_routes import inventory_bp
from routes.analytics_routes import analytics_bp

# Create a blueprint for all routes
all_routes_bp = Blueprint("all_routes", __name__)

# Register all blueprints
def register_routes(app):
    """Register all route blueprints with the Flask app."""
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(inventory_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    
    # You can add more blueprints here as needed
    
    return app
