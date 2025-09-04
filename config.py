"""
LinkForge Configuration
======================

Simple configuration management for the URL shortener.
Only includes settings for implemented features.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration with all settings for implemented features only."""

    # Flask core settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL', 'linkforge.db')

    # Session management
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True

    # Password requirements
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 15

    # Link settings
    MAX_LINKS_PER_USER = 1000

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

def get_config():
    """Get configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'development')

    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()

config = get_config()
