"""
LinkForge Complete - Main Application
====================================

Modular Flask URL shortener with all features implemented:
- Dynamic link management (core feature)
- Link expiration with enforcement
- Password protection with enforcement
- Bulk operations and QR codes
- Complete analytics and export

Entry point for the application.
"""

from flask import Flask, session, request, jsonify
from config import get_config
import os

def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    config = get_config()
    app.config.from_object(config)


    # --- Security Headers and CORS Setup ---
    # These headers help protect your app from common web attacks:
    # - X-Frame-Options: Prevents clickjacking by disallowing your site in iframes
    # - X-Content-Type-Options: Prevents MIME type sniffing
    # - Content-Security-Policy: Restricts sources for scripts, styles, etc.
    # CORS (Cross-Origin Resource Sharing) controls which domains can access your API/resources
    # Flask-CORS is used here to allow only same-origin requests (default)
    from flask_cors import CORS
    # Set allowed CORS origin from environment variable for flexibility
    # Example in .env: CORS_ALLOWED_ORIGIN=https://yourdomain.com
    cors_origin = os.environ.get('CORS_ALLOWED_ORIGIN', 'http://localhost:5000')
    CORS(app, resources={r"/*": {"origins": cors_origin}})  # Restricts CORS to env value

    @app.after_request
    def set_security_headers(response):
        # Prevents your site from being loaded in an iframe (clickjacking)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # Prevents browsers from MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Basic Content Security Policy (CSP) to restrict sources
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
        return response

    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.links import links_bp  
    from blueprints.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(main_bp)

    # Initialize database
    from models import DatabaseManager
    with app.app_context():
        db = DatabaseManager()

    # Template context processor
    @app.context_processor
    def inject_template_vars():
        """Add common variables to all templates."""
        return {
            'app_name': 'LinkForge',
            'current_year': 2025,
            'is_authenticated': 'user_id' in session
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return app.send_static_file('404.html') if os.path.exists('static/404.html') else ('Not Found', 404)

    @app.errorhandler(500)
    def internal_error(error):
        return 'Internal Server Error', 500

    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🔗 LinkForge Complete starting...")
    print(f"📡 Server: http://localhost:{port}")
    print("✅ All features implemented and ready!")

    app.run(debug=True, host='0.0.0.0', port=port)
