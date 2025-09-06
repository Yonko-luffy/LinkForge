"""
Database Connection Management - Backend Pattern
===============================================

🎓 **EDUCATIONAL OVERVIEW:**
This module demonstrates Flask's request-scoped database connection pattern,
an approach used in applications for efficient resource management.

🏗️ **KEY CONCEPTS DEMONSTRATED:**
1. Request-Scoped Connections - Flask's 'g' object pattern
2. Connection Management - Reusing connections efficiently  
3. Resource Management - Automatic cleanup and teardown
4. SQLite Integration - Database patterns
5. Row Factory - Enhanced result handling with dictionary-like access

🎯 **INTERVIEW TALKING POINTS:**
- "I use Flask's g object for request-scoped database connections to optimize performance"
- "This pattern prevents connection leaks and reduces database overhead"
- "Row factory provides dictionary-like access to query results"
- "Automatic cleanup ensures resources are properly released"
"""

import psycopg2
import psycopg2.extras
from flask import g
import os
import os

def get_db_connection():
    """
    🔗 REQUEST-SCOPED DATABASE CONNECTION
    ====================================
    
    Get database connection using Flask's request-scoped 'g' object.
    
    📚 **WHAT IS FLASK'S 'g' OBJECT?**
    Flask's 'g' object is a request-scoped storage mechanism that persists
    data for the duration of a single request across all functions called.
    
    🎯 **WHY USE REQUEST-SCOPED CONNECTIONS?**
    1. **Performance**: Reuses connection within a single request
    2. **Resource Efficiency**: Prevents creating multiple connections per request
    3. **Automatic Cleanup**: Connection is automatically cleaned up after request
    4. **Thread Safety**: Each request gets its own connection
    5. **Common Pattern**: Used in Flask applications
    
    🔄 **CONNECTION LIFECYCLE:**
    1. First call in request → Create connection, store in g.db_conn
    2. Subsequent calls → Return existing connection from g.db_conn  
    3. End of request → Flask calls teardown handler to close connection
    
    📖 **INTERVIEW EXPLANATION:**
    "I use Flask's g object to store database connections per request. This ensures
    efficient resource usage by reusing connections within a request while
    automatically cleaning them up when the request ends."
    
    Returns:
        psycopg2.Connection: Database connection with RealDictCursor factory
    """
    # Check if connection already exists in this request's context
    if 'db_conn' not in g:
        # Create new connection and store in Flask's g object
        # 
        # 🔧 **POSTGRESQL CONNECTION DETAILS:**
        # - Uses DATABASE_URL environment variable for flexibility
        # - RealDictCursor provides dictionary-like access to results
        # - Connection persists for entire request lifecycle
        g.db_conn = psycopg2.connect(
            os.environ.get('DATABASE_URL'),
            cursor_factory=psycopg2.extras.RealDictCursor  # Enables dict-like result access
        )
    
    # Return the connection (either newly created or existing)
    return g.db_conn

def get_db_cursor():
    """
    🎯 DATABASE CURSOR FACTORY
    ==========================
    
    Get database cursor from the request-scoped connection.
    
    📚 **WHAT IS A DATABASE CURSOR?**
    A cursor is an object that allows you to execute SQL statements and fetch results.
    It's the interface between your Python code and the database.
    
    🎯 **WHY USE A CURSOR FACTORY?**
    1. **Consistency**: All database operations use the same connection
    2. **Simplicity**: One function call gets you a ready-to-use cursor
    3. **RealDictCursor Benefits**: Results accessible as dictionaries
    4. **Common Pattern**: Standard practice in Flask applications
    
    📖 **INTERVIEW EXPLANATION:**
    "This factory function provides a consistent way to get database cursors
    that are connected to our request-scoped connection. Using RealDictCursor
    makes the results easier to work with by providing dictionary-like access."
    
    Returns:
        psycopg2.extras.RealDictCursor: Database cursor for executing queries
    """
    # Get cursor from the request-scoped connection
    # The cursor inherits Row factory from the connection
    return get_db_connection().cursor()

def close_db(error=None):
    """
    🧹 REQUEST CLEANUP HANDLER
    ==========================
    
    Close database connection at the end of each request.
    
    📚 **FLASK TEARDOWN PATTERN:**
    This function is registered as a teardown handler with Flask.
    Flask automatically calls it at the end of every request.
    
    🎯 **WHY AUTOMATIC CLEANUP?**
    1. **Resource Management**: Prevents connection leaks
    2. **Memory Efficiency**: Frees up database connections
    3. **Reliability**: Guaranteed cleanup even if errors occur
    4. **Common Practice**: Standard pattern in applications
    
    🔄 **CLEANUP PROCESS:**
    1. Extract connection from g object (if it exists)
    2. Close the connection if one was created
    3. Connection is removed from g object automatically
    
    📖 **INTERVIEW EXPLANATION:**
    "This teardown handler ensures database connections are properly closed
    after each request. It's registered with Flask to run automatically,
    providing reliable resource cleanup even if errors occur."
    
    Args:
        error: Any error that occurred during the request (unused but required by Flask)
    """
    # Extract connection from g object (returns None if not found)
    # pop() removes the key from g, preventing memory leaks
    db = g.pop('db_conn', None)
    
    # Close connection if one was created during this request
    if db is not None:
        db.close()

def init_db_app(app):
    """
    🏗️ FLASK APPLICATION INTEGRATION
    ================================
    
    Initialize database connection management with Flask application.
    
    📚 **APPLICATION FACTORY INTEGRATION:**
    This function integrates our database connection pattern with a Flask app
    created using the application factory pattern.
    
    🎯 **REGISTRATION PROCESS:**
    Registers the close_db function as a teardown handler, ensuring it runs
    after every request to clean up database connections.
    
    📖 **INTERVIEW EXPLANATION:**
    "This function integrates our database connection management with the Flask
    application by registering our cleanup handler. This ensures proper resource
    management across the entire application lifecycle."
    
    Args:
        app (Flask): Flask application instance to configure
    """
    # Register close_db as a teardown handler
    # Flask will call this function after every request
    app.teardown_appcontext(close_db)

# 🎯 **ADVANCED PATTERNS FOR INTERVIEW DISCUSSION:**
# =================================================
# 
# 💡 **CONNECTION POOLING:**
# In high-traffic production applications, you might use connection pooling:
# 
# from psycopg2 import pool
# 
# class DatabasePool:
#     def __init__(self, min_conn=1, max_conn=10):
#         self.pool = psycopg2.pool.ThreadedConnectionPool(
#             min_conn, max_conn, DATABASE_URL
#         )
# 
# 💡 **TRANSACTION MANAGEMENT:**
# For complex operations, you might add transaction support:
# 
# @contextmanager
# def get_db_transaction():
#     conn = get_db_connection()
#     try:
#         yield conn.cursor()
#         conn.commit()
#     except Exception:
#         conn.rollback()
#         raise
# 
# 💡 **DATABASE HEALTH CHECKS:**
# Production applications often include health check endpoints:
# 
# def check_database_health():
#     try:
#         cursor = get_db_cursor()
#         cursor.execute('SELECT 1')
#         return True
#     except Exception:
#         return False
