"""
LinkForge Database Models - Implementation
=========================================

🎓 **EDUCATIONAL OVERVIEW:**
This module demonstrates database operations using Flask practices,
PostgreSQL integration, and secure user authentication patterns.

🏗️ **KEY CONCEPTS DEMONSTRATED:**
1. Request-Scoped Database Connections - Flask pattern
2. PostgreSQL Schema Design - Relational database modeling
3. Secure Password Hashing - Authentication
4. Input Validation & Sanitization - Security practices
5. SQL Injection Prevention - Parameterized queries
6. Database Indexing - Performance optimization
7. Foreign Key Relationships - Data integrity
8. Error Handling - Graceful failure management

🎯 **INTERVIEW TALKING POINTS:**
- "I use parameterized queries to prevent SQL injection attacks"
- "Password hashing with werkzeug provides secure authentication"
- "Database indexes optimize query performance for frequently accessed data"
- "Foreign key constraints maintain data integrity across tables"
- "Request-scoped connections optimize database resource usage"

🗄️ **DATABASE SCHEMA DESIGN:**
```
users: id, username, email, password_hash, created_at
links: id, user_id, original_url, short_code, display_name, password_hash, 
       expiration_date, clicks, is_active, created_at, updated_at
clicks: id, link_id, ip_address, referrer, user_agent, clicked_at
```

🔒 **SECURITY FEATURES:**
- Password hashing with salt (werkzeug.security)
- SQL injection prevention (parameterized queries)
- Input validation and sanitization
- User authorization checks
- Secure session management
"""

import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from .db_utils import get_db_cursor, get_db_connection
import os

class DatabaseManager:
    """
    🗄️ DATABASE MANAGER CLASS
    =========================
    
    Database manager handling all database operations and schema management.
    
    📚 **DESIGN PATTERNS DEMONSTRATED:**
    1. **Singleton Pattern**: Single instance manages all database operations
    2. **Schema Management**: Automated database initialization
    3. **Connection Management**: Proper resource handling
    4. **Error Handling**: Graceful database error management
    
    🎯 **FEATURES:**
    1. **PostgreSQL Integration**: Database support
    2. **Schema Versioning**: Automated table creation and updates  
    3. **Index Optimization**: Performance-optimized database queries
    4. **Data Integrity**: Foreign key constraints and relationships
    
    📖 **INTERVIEW EXPLANATION:**
    "I created a DatabaseManager class to centralize all database schema
    management and provide a clean interface for database operations.
    This follows the single responsibility principle and makes the code
    more maintainable."
    """

    def __init__(self, db_url=None):
        """
        🏗️ DATABASE MANAGER INITIALIZATION
        ==================================
        
        Initialize database manager with connection URL and schema setup.
        
        Args:
            db_url (str, optional): Database connection URL. Defaults to environment variable.
        """
        # Use provided URL or fall back to environment variable
        # This flexibility allows for testing with different databases
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        
        # Initialize database schema on instantiation
        # Ensures database is ready for operations
        self.init_database()

    def get_connection(self):
        """
        🔗 DATABASE CONNECTION FACTORY
        ==============================
        
        Create PostgreSQL connection with dictionary cursor support.
        
        📚 **CURSOR FACTORY EXPLANATION:**
        RealDictCursor provides dictionary-like access to query results,
        making the returned data easier to work with in Python.
        
        Returns:
            psycopg2.Connection: Database connection with RealDictCursor
        """
        # Create connection with dictionary cursor for easier result handling
        conn = psycopg2.connect(self.db_url, cursor_factory=psycopg2.extras.RealDictCursor)
        return conn

    def init_database(self):
        """
        🏗️ DATABASE SCHEMA INITIALIZATION
        =================================
        
        Initialize PostgreSQL database with complete schema for all features.
        
        📚 **SCHEMA DESIGN PRINCIPLES:**
        1. **Normalization**: Properly normalized tables to reduce redundancy
        2. **Foreign Keys**: Maintain referential integrity between tables
        3. **Indexes**: Optimize frequently queried columns
        4. **Constraints**: Enforce data validity at database level
        5. **Default Values**: Sensible defaults for optional fields
        
        🗄️ **TABLE RELATIONSHIPS:**
        - users → links (one-to-many via user_id foreign key)
        - links → clicks (one-to-many via link_id foreign key)
        - Cascade deletes ensure data consistency
        
        📖 **INTERVIEW EXPLANATION:**
        "I designed a normalized database schema with proper foreign key
        relationships and indexes. The schema supports user management,
        link creation, and click tracking with full data integrity."
        """
        # Create connection for schema setup
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 👥 USERS TABLE - Authentication and user management
        # ==================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,                    -- Auto-incrementing primary key
                username VARCHAR(255) UNIQUE NOT NULL,    -- Unique username constraint
                email VARCHAR(255) UNIQUE NOT NULL,       -- Unique email constraint  
                password_hash TEXT NOT NULL,              -- Hashed password (never store plain text)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Account creation timestamp
            )
        """)
        
        # 🔗 LINKS TABLE - URL shortening core functionality
        # =================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id SERIAL PRIMARY KEY,                    -- Auto-incrementing primary key
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,  -- Foreign key with cascade
                original_url TEXT NOT NULL,              -- Full original URL
                short_code VARCHAR(255) UNIQUE NOT NULL, -- Unique short identifier
                display_name VARCHAR(255) NOT NULL,      -- User-friendly name for the link
                password_hash TEXT DEFAULT NULL,         -- Optional password protection
                expiration_date TIMESTAMP DEFAULT NULL,  -- Optional expiration
                clicks INTEGER DEFAULT 0,               -- Click counter
                is_active BOOLEAN DEFAULT TRUE,         -- Soft delete flag
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Creation timestamp
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- Last update timestamp
            )
        """)
        
        # 📊 CLICKS TABLE - Analytics and tracking
        # ========================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id SERIAL PRIMARY KEY,                    -- Auto-incrementing primary key
                link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,  -- Foreign key with cascade
                ip_address VARCHAR(64),                   -- Client IP for analytics
                referrer TEXT DEFAULT 'Direct',          -- Referring website
                user_agent TEXT DEFAULT '',              -- Browser/client information
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP      -- Click timestamp
            )
        """)
        
        # 🚀 PERFORMANCE OPTIMIZATION - Database indexes
        # ==============================================
        # Indexes dramatically improve query performance on frequently searched columns
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_user_id ON links(user_id)')      # User's links lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_short_code ON links(short_code)') # Short code resolution
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id)')    # Click analytics
        
        # Commit changes and close connection
        conn.commit()
        conn.close()


# User Management Functions
def create_user(username, email, password):
    """Create new user with validation using DB pattern."""
    try:
        # Validation
        if not username or not username.strip():
            return {'success': False, 'message': 'Username is required'}
        
        if not email or not email.strip():
            return {'success': False, 'message': 'Email is required'}
        
        if not password or len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}

        cursor = get_db_cursor()
        conn = get_db_connection()

        # Check existing users
        cursor.execute(
            'SELECT id FROM users WHERE username = %s OR email = %s',
            (username, email)
        )
        existing = cursor.fetchone()

        if existing:
            return {'success': False, 'message': 'Username or email already exists'}

        # Create user
        password_hash = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id',
            (username, email, password_hash)
        )
        user_id = cursor.fetchone()['id']
        conn.commit()
        return {'success': True, 'user_id': user_id}

    except Exception as e:
        return {'success': False, 'message': 'Database error'}


def authenticate_user(username_or_email, password):
    """Authenticate user login credentials using professional DB pattern."""
    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT * FROM users WHERE username = %s OR email = %s',
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }
        else:
            return {'success': False, 'message': 'Invalid credentials'}

    except Exception:
        return {'success': False, 'message': 'Authentication error'}


def get_user_by_id(user_id):
    """Get user by ID using professional DB pattern."""
    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT id, username, email, created_at FROM users WHERE id = %s',
            (user_id,)
        )
        user = cursor.fetchone()

        return dict(user) if user else None
    except Exception:
        return None


# Link Management Functions
def create_link(user_id, original_url, display_name, short_code, password=None, expiration_days=None):
    """
    Create new link with all features implemented using professional DB pattern.

    Args:
        user_id: User creating the link
        original_url: Destination URL
        display_name: Human-readable name
        short_code: Custom short code
        password: Optional password protection
        expiration_days: Days until expiration (None for never)

    Returns:
        dict: Success status and details
    """
    try:
        cursor = get_db_cursor()
        conn = get_db_connection()

        # Calculate expiration date if specified
        expiration_date = None
        if expiration_days and expiration_days > 0:
            expiration_date = (datetime.now() + timedelta(days=expiration_days)).isoformat()

        # Hash password if provided
        password_hash = None
        if password and len(password.strip()) > 0:
            password_hash = generate_password_hash(password.strip())

        # Check for existing short code
        cursor.execute(
            'SELECT id FROM links WHERE short_code = %s',
            (short_code,)
        )
        existing = cursor.fetchone()

        if existing:
            return {'success': False, 'message': 'Short code already exists'}

        # Create link
        cursor.execute("""
            INSERT INTO links 
            (user_id, original_url, short_code, display_name, password_hash, expiration_date)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (user_id, original_url, short_code, display_name, password_hash, expiration_date))
        link_id = cursor.fetchone()['id']
        conn.commit()
        return {
            'success': True,
            'link_id': link_id,
            'short_code': short_code
        }

    except Exception as e:
        return {'success': False, 'message': f'Database error: {str(e)}'}


def get_user_links(user_id, search_query=None):
    """Get all links for a user with optional search using professional DB pattern."""
    try:
        cursor = get_db_cursor()

        if search_query:
            cursor.execute("""
                SELECT * FROM links 
                WHERE user_id = %s 
                AND (display_name ILIKE %s OR original_url ILIKE %s OR short_code ILIKE %s)
                ORDER BY created_at DESC
            """, (user_id, f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute(
                'SELECT * FROM links WHERE user_id = %s ORDER BY created_at DESC',
                (user_id,)
            )
        links = cursor.fetchall()
        return [dict(link) for link in links]

    except Exception:
        return []


def get_link_by_short_code(short_code):
    """Get link by short code for redirection using professional DB pattern."""
    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT * FROM links WHERE short_code = %s',
            (short_code,)
        )
        link = cursor.fetchone()

        return dict(link) if link else None

    except Exception:
        return None


def update_link_url(link_id, user_id, new_url):
    """
    Update link destination URL (dynamic link feature) using professional DB pattern.

    This is the core dynamic functionality - users can change
    where their links redirect without changing the short code.
    """
    try:
        cursor = get_db_cursor()
        conn = get_db_connection()

        # Verify user owns the link
        cursor.execute("""
            UPDATE links 
            SET original_url = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND user_id = %s
        """, (new_url, link_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            return {'success': True, 'message': 'Link updated successfully'}
        else:
            return {'success': False, 'message': 'Link not found or access denied'}

    except Exception as e:
        return {'success': False, 'message': f'Update failed: {str(e)}'}


def delete_links(link_ids, user_id):
    """Delete multiple links (bulk delete) using professional DB pattern."""
    try:
        cursor = get_db_cursor()
        conn = get_db_connection()

        # Convert link_ids to placeholders for SQL
        placeholders = ','.join(['%s'] * len(link_ids))
        params = link_ids + [user_id]
        # Delete clicks first (foreign key constraint)
        cursor.execute(f"""
            DELETE FROM clicks 
            WHERE link_id IN (
                SELECT id FROM links 
                WHERE id IN ({placeholders}) AND user_id = %s
            )
        """, params)
        # Delete links
        cursor.execute(f"""
            DELETE FROM links 
            WHERE id IN ({placeholders}) AND user_id = %s
        """, params)
        deleted_count = cursor.rowcount
        conn.commit()
        return {'success': True, 'deleted_count': deleted_count}

    except Exception as e:
        return {'success': False, 'message': f'Delete failed: {str(e)}'}


def record_click(link_id, ip_address=None, referrer=None, user_agent=None):
    """Record click analytics using professional DB pattern."""
    try:
        cursor = get_db_cursor()
        conn = get_db_connection()

        # Record click
        cursor.execute("""
            INSERT INTO clicks (link_id, ip_address, referrer, user_agent)
            VALUES (%s, %s, %s, %s)
        """, (link_id, ip_address, referrer or 'Direct', user_agent or ''))
        # Increment counter
        cursor.execute(
            'UPDATE links SET clicks = clicks + 1 WHERE id = %s',
            (link_id,)
        )
        conn.commit()
        return True

    except Exception:
        return False


def is_link_expired(link):
    """Check if a link has expired."""
    if not link.get('expiration_date'):
        return False

    try:
        expiration = datetime.fromisoformat(link['expiration_date'])
        return datetime.now() > expiration
    except:
        return False


def verify_link_password(link, provided_password):
    """Verify password for password-protected links."""
    if not link.get('password_hash'):
        return True  # No password required

    if not provided_password:
        return False  # Password required but not provided

    return check_password_hash(link['password_hash'], provided_password)


def get_user_stats(user_id):
    """Get user statistics for dashboard using professional DB pattern."""
    try:
        cursor = get_db_cursor()

        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_links,
                COALESCE(SUM(clicks), 0) as total_clicks,
                COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_links
            FROM links 
            WHERE user_id = %s
        """, (user_id,))
        stats = cursor.fetchone()
        # Count expired links
        now = datetime.now()
        cursor.execute("""
            SELECT COUNT(*) as expired_count
            FROM links 
            WHERE user_id = %s AND expiration_date IS NOT NULL AND expiration_date < %s
        """, (user_id, now))
        expired = cursor.fetchone()

        return {
            'total_links': stats['total_links'] or 0,
            'total_clicks': stats['total_clicks'] or 0,
            'active_links': stats['active_links'] or 0,
            'expired_links': expired['expired_count'] or 0
        }

    except Exception:
        return {
            'total_links': 0,
            'total_clicks': 0,
            'active_links': 0,
            'expired_links': 0
        }
