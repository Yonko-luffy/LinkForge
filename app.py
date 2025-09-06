"""
LinkForge - Flask Application Entry Point
=========================================

URL shortener demonstrating Flask patterns:

🏗️ **ARCHITECTURE OVERVIEW:**
- Application Factory Pattern: Separates app creation from configuration
- Blueprint Organization: Modular route organization for scalability  
- Database Patterns: Request-scoped connections with automatic cleanup
- Security Integration: CORS, security headers, and input validation
- Environment Configuration: Environment-based configuration and error handling

🎯 **LEARNING OBJECTIVES:**
This structure demonstrates Flask development practices used in:
- Web applications
- Modular architectures  
- Environment-based deployments
- Team-based development

Entry point for the LinkForge URL shortener application.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from linkforge import create_app
from linkforge.models import DatabaseManager

# 🏭 APPLICATION FACTORY PATTERN
# ===============================
# The create_app() function is called an "Application Factory"
# This is a Flask pattern that separates app creation from configuration
# 
# Benefits:
# - Easier testing (can create multiple app instances with different configs)
# - Better for deployment (app creation happens at startup)
# - Cleaner code organization (configuration logic separated from app logic)
# - Supports multiple environments (dev, staging, prod) with different configs

app = create_app()

# 🗄️ DATABASE INITIALIZATION
# ===========================
# Initialize database schema on application startup
# This ensures all required tables exist before handling requests
# 
# Note:
# - In larger applications, database migrations are typically handled separately
# - This pattern works well for portfolio projects and development
# - For larger apps, consider using Flask-Migrate for schema changes

db_manager = DatabaseManager()

# 🚀 DEVELOPMENT SERVER STARTUP
# ==============================
# This block only runs when the file is executed directly (not imported)
# In production, a WSGI server like Gunicorn would handle this instead

if __name__ == '__main__':
    # 🔧 Environment Configuration
    # Extract port from environment variable (required for Heroku deployment)
    import os
    port = int(os.environ.get('PORT', 5000))
    
    # 🐛 Debug Mode Control
    # Debug mode should NEVER be True in production
    # It exposes sensitive information and allows code execution
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 🌐 Server Binding
    # host='0.0.0.0' allows external connections (required for cloud deployment)
    # In development, this allows access from other devices on your network
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

