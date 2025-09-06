"""
LinkForge - URL Shortener Package
=================================

🎓 **EDUCATIONAL OVERVIEW:**
This module demonstrates the Flask Application Factory Pattern, an approach 
to creating Flask applications that separates app creation from configuration.

🏗️ **KEY CONCEPTS DEMONSTRATED:**
1. Application Factory Pattern - Organized Flask architecture
2. Blueprint Registration - Modular route organization  
3. Security Integration - CORS and security headers
4. Database Connection Management - Request-scoped patterns
5. Package Structure - Organized application layout

🎯 **INTERVIEW TALKING POINTS:**
- "I implemented the application factory pattern for better testability and deployment flexibility"
- "The package structure follows Flask best practices for applications"
- "Security is handled through CORS and proper request-scoped database connections"
"""

from flask import Flask, render_template
from flask_cors import CORS
from .config import Config
from .db_utils import close_db

def create_app():
    """
    🏭 APPLICATION FACTORY FUNCTION
    ================================
    
    This function implements the Flask Application Factory Pattern.
    
    📚 **WHAT IS APPLICATION FACTORY PATTERN?**
    Instead of creating the Flask app at the module level, we create it inside a function.
    This provides several benefits:
    
    🎯 **BENEFITS:**
    1. **Testing**: Can create multiple app instances with different configurations
    2. **Deployment**: App creation happens at startup, not at import time
    3. **Environment Handling**: Different configs for dev/staging/production
    4. **Modularity**: Cleaner separation of concerns
    
    📖 **INTERVIEW EXPLANATION:**
    "I used the application factory pattern because it makes the application more 
    testable and allows for different configurations in different environments.
    This is a Flask best practice used in production applications."
    """
    
    # 🏗️ FLASK APP CREATION
    # =====================
    # Create Flask instance with explicit template and static folder paths
    # This ensures the app can find its resources regardless of where it's run from
    app = Flask(__name__, 
                template_folder='templates',  # HTML templates location
                static_folder='static')       # CSS, JS, images location
    
    # 📋 CONFIGURATION LOADING
    # ========================
    # Load configuration from our Config class
    # This centralizes all app settings in one place
    app.config.from_object(Config)
    
    # 🔒 SECURITY: CORS (Cross-Origin Resource Sharing) SETUP
    # =======================================================
    # CORS controls which domains can access your API/resources from a browser
    # 
    # 🚨 **SECURITY EXPLANATION:**
    # Without CORS, any website could make requests to your API from a user's browser
    # CORS restricts this to only allowed origins for security
    # 
    # 📖 **INTERVIEW EXPLANATION:**
    # "I implemented CORS to control cross-origin requests. This prevents other 
    # websites from making unauthorized requests to our API from users' browsers."
    CORS(app)
    
    # 🧩 BLUEPRINT REGISTRATION
    # =========================
    # Blueprints are Flask's way of organizing routes into modules
    # This keeps code organized and makes it easier to maintain large applications
    # 
    # 📖 **INTERVIEW EXPLANATION:**
    # "I used Flask blueprints to organize routes into logical modules. This makes
    # the codebase more maintainable and follows the separation of concerns principle."
    
    # Import blueprints using relative imports (Python package practice)
    from .blueprints.main import main_bp      # Landing page and static routes
    from .blueprints.auth import auth_bp      # User authentication (login/register)
    from .blueprints.links import links_bp    # URL shortening functionality
    
    # Register blueprints with the Flask application
    app.register_blueprint(main_bp)                    # No URL prefix (root routes)
    app.register_blueprint(auth_bp, url_prefix='/auth') # All auth routes start with /auth
    app.register_blueprint(links_bp)                   # No prefix (main functionality)
    
    # 🗄️ DATABASE CONNECTION MANAGEMENT
    # =================================
    # Register the database connection teardown handler
    # This ensures database connections are properly closed after each request
    # 
    # 📖 **INTERVIEW EXPLANATION:**
    # "I implemented request-scoped database connections using Flask's g object.
    # This ensures efficient resource management and prevents connection leaks."
    app.teardown_appcontext(close_db)
    
    # 🔒 SECURITY HEADERS MIDDLEWARE
    # ==============================
    # Add security headers to all responses
    # These headers provide protection against common web vulnerabilities
    @app.after_request
    def add_security_headers(response):
        """
        Add security headers to all responses.
        
        🛡️ **SECURITY HEADERS EXPLAINED:**
        - X-Frame-Options: Prevents clickjacking attacks
        - X-Content-Type-Options: Prevents MIME type sniffing
        - Content-Security-Policy: Controls resource loading
        - X-XSS-Protection: Basic XSS protection for older browsers
        """
        # Prevent clickjacking - stops your site being embedded in iframes
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing - forces browsers to respect declared content types
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Basic XSS protection for older browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy - controls what resources can be loaded
        # This policy allows:
        # - Scripts and styles from same origin and inline
        # - Images from anywhere (for QR codes, user content)
        # - Fonts from same origin and data URIs
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: *; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )
        
        return response
    
    # 🚨 GLOBAL ERROR HANDLERS
    # ========================
    # Centralized error handling for consistent user experience
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        return render_template('500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return render_template('403.html'), 403

    # 🎯 RETURN THE CONFIGURED APP
    # ============================
    # Return the fully configured Flask application
    # The calling code can then run this app or use it for testing
    return app
