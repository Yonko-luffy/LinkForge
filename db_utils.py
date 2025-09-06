"""
Database Connection Management - Professional Backend Pattern
============================================================

Flask best practice for database connections using request-scoped connections.
This eliminates connection overhead and demonstrates professional backend skills.
"""

import psycopg2
import psycopg2.extras
from flask import g
import os

def get_db_connection():
    """
    Get database connection using Flask's request-scoped 'g' object.
    
    This is a professional pattern that:
    - Reuses connections within a single request
    - Automatically handles connection cleanup
    - Reduces database overhead
    - Follows Flask best practices
    """
    if 'db_conn' not in g:
        g.db_conn = psycopg2.connect(
            os.environ.get('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
    return g.db_conn

def get_db_cursor():
    """Get database cursor from request-scoped connection."""
    return get_db_connection().cursor()

def close_db(error=None):
    """Close database connection at end of request."""
    db = g.pop('db_conn', None)
    if db is not None:
        db.close()

def init_db_app(app):
    """Initialize database connection management with Flask app."""
    app.teardown_appcontext(close_db)
