"""
LinkForge Configuration Module
=============================

🎓 **EDUCATIONAL OVERVIEW:**
This module demonstrates Flask configuration management using classes
and environment variables following common practices.

🏗️ **KEY CONCEPTS DEMONSTRATED:**
1. Environment Variable Configuration - 12-Factor App Principles
2. Security Best Practices - Secret key and session management
3. Multiple Environment Support - Development vs Production configs
4. Configuration Inheritance - Object-oriented config design
5. Type Safety - Structured configuration over dictionaries

🎯 **INTERVIEW TALKING POINTS:**
- "I use environment variables for configuration following 12-Factor App principles"
- "Multiple config classes support different deployment environments"
- "Security settings like session cookies are properly configured"
- "Configuration is type-safe and well-documented"
"""

import os
from datetime import timedelta

class Config:
    """
    🔧 BASE CONFIGURATION CLASS
    ===========================
    
    This base class contains all the common configuration settings.
    Other environment-specific classes inherit from this.
    
    📚 **WHY USE CONFIGURATION CLASSES?**
    1. **Organization**: All settings centralized and documented
    2. **Type Safety**: Better than dictionary-based configuration
    3. **Inheritance**: Environment-specific configs can override base settings
    4. **IDE Support**: Auto-completion and error checking
    5. **Documentation**: Each setting can be clearly explained
    
    🔒 **SECURITY PRINCIPLES DEMONSTRATED:**
    1. **Environment Variables**: Sensitive data comes from environment
    2. **Secure Defaults**: Safe fallback values for development
    3. **Session Security**: Proper cookie configuration
    4. **No Hardcoding**: Production secrets never in source code
    
    📖 **INTERVIEW EXPLANATION:**
    "I structured configuration using classes because it provides better organization,
    type safety, and allows for environment-specific overrides while maintaining
    a secure approach to sensitive data management."
    """

    # 🔐 FLASK CORE SECURITY SETTINGS
    # ===============================
    # Secret key is critical for Flask security - used for:
    # - Session cookie signing (prevents tampering)
    # - CSRF token generation (if implemented)
    # - Secure cookie encryption
    # 
    # 🚨 **PRODUCTION SECURITY NOTE:**
    # The fallback value should NEVER be used in production!
    # Always set SECRET_KEY environment variable with a cryptographically secure random value
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    
    # Debug mode configuration - automatically determined from environment
    # Setting this via environment allows easy switching between modes
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # 🗄️ DATABASE CONFIGURATION
    # =========================
    # Database URL supports multiple database types:
    # - PostgreSQL: 'postgresql://user:pass@host:port/dbname' (recommended)
    # - MySQL: 'mysql://user:pass@host:port/dbname'
    # 
    # 📖 **INTERVIEW EXPLANATION:**
    # "Using DATABASE_URL environment variable allows the same code to work
    # with different databases across environments without code changes."
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/linkforge')

    # 🍪 SESSION MANAGEMENT CONFIGURATION
    # ===================================
    # Session handling with security considerations
    
    # Session lifetime - how long user stays logged in
    # 24 hours is reasonable for a URL shortener application
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # HttpOnly cookies prevent JavaScript access (XSS protection)
    # This is a security best practice to prevent session hijacking
    SESSION_COOKIE_HTTPONLY = True

    # 🔒 PASSWORD SECURITY REQUIREMENTS
    # =================================
    # Define password complexity requirements
    # These can be easily adjusted without changing validation logic
    MIN_PASSWORD_LENGTH = 6    # Minimum for basic security
    MAX_PASSWORD_LENGTH = 15   # Reasonable upper limit for usability

    # 📊 APPLICATION BUSINESS LOGIC SETTINGS
    # ======================================
    # Maximum links per user - prevents abuse and manages database size
    # This demonstrates how business rules can be configured
    MAX_LINKS_PER_USER = 1000

class DevelopmentConfig(Config):
    """
    🔧 DEVELOPMENT ENVIRONMENT CONFIGURATION
    ========================================
    
    Configuration optimized for local development.
    
    📚 **DEVELOPMENT-SPECIFIC FEATURES:**
    1. **Debug Mode**: Enhanced error pages and auto-reload
    2. **Relaxed Security**: Easier testing and development
    3. **Local Database**: SQLite for simplicity
    
    📖 **INTERVIEW EXPLANATION:**
    "Development config inherits all base settings but can override them
    for development convenience while maintaining security awareness."
    """
    # All settings inherited from Config class
    # DEBUG is already handled via environment variable in base class
    pass

class ProductionConfig(Config):
    """
    🔧 PRODUCTION ENVIRONMENT CONFIGURATION
    =======================================
    
    Configuration optimized for production deployment.
    
    🔒 **PRODUCTION SECURITY ENHANCEMENTS:**
    1. **Debug Disabled**: No sensitive information in error pages
    2. **Secure Cookies**: HTTPS-only session cookies
    3. **Environment Variables**: All sensitive data from environment
    
    📖 **INTERVIEW EXPLANATION:**
    "Production config enforces security best practices like secure cookies
    and disables debug mode to prevent information leakage."
    """
    # Force debug mode off in production for security
    DEBUG = False
    
    # Require HTTPS for session cookies in production
    # This prevents session hijacking over insecure connections
    SESSION_COOKIE_SECURE = True

def get_config():
    """
    🎯 CONFIGURATION FACTORY FUNCTION
    =================================
    
    Returns the appropriate configuration class based on environment.
    
    📚 **DYNAMIC CONFIGURATION LOADING:**
    This function demonstrates how to dynamically select configuration
    based on the deployment environment.
    
    🌍 **ENVIRONMENT DETECTION:**
    - Uses FLASK_ENV environment variable
    - Defaults to development for safety
    - Production must be explicitly set
    
    📖 **INTERVIEW EXPLANATION:**
    "This factory function automatically selects the right configuration
    for the current environment, making deployment easier and reducing
    the chance of configuration errors."
    
    Returns:
        Config: Appropriate configuration instance for current environment
    """
    # Get environment from environment variable
    env = os.environ.get('FLASK_ENV', 'development')

    # Return appropriate configuration class
    if env == 'production':
        return ProductionConfig()
    else:
        # Default to development config for safety
        # Better to be overly permissive in dev than overly restrictive
        return DevelopmentConfig()

# 🎯 **EXTENSIBILITY NOTES:**
# ==========================
# This configuration system can easily be extended for additional environments:
# 
# class TestingConfig(Config):
#     """Configuration for automated testing."""
#     TESTING = True
#     DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for fast tests
# 
# class StagingConfig(ProductionConfig):
#     """Configuration for staging environment."""
#     DEBUG = True  # Allow debugging in staging
#
# Additional settings that could be added:
# - MAIL_SERVER configuration for email features
# - CACHE_TYPE for caching configuration  
# - RATE_LIMIT settings for API protection
# - LOGGING configuration for different environments
