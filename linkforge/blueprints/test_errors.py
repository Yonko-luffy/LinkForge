"""
Error Template Viewer - Temporary Testing Route
===============================================

This file creates test routes to view error templates.
Add this to your main blueprint temporarily to test error pages.
"""

from flask import Blueprint, render_template, session

# Create a test blueprint
test_bp = Blueprint('test', __name__)

@test_bp.route('/test/404')
def test_404():
    """View the 404 error page."""
    return render_template('404.html'), 200  # Return 200 so we can see it

@test_bp.route('/test/500') 
def test_500():
    """View the 500 error page."""
    return render_template('500.html'), 200  # Return 200 so we can see it

@test_bp.route('/test/403')
def test_403():
    """View the 403 error page."""
    return render_template('403.html'), 200  # Return 200 so we can see it

@test_bp.route('/test/errors')
def test_errors_menu():
    """Menu to view all error pages."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error Templates Viewer</title>
        <style>
            body { 
                font-family: system-ui, sans-serif; 
                background: #000; 
                color: #fff; 
                padding: 2rem; 
                text-align: center;
            }
            .menu { 
                max-width: 600px; 
                margin: 0 auto; 
                background: #111; 
                padding: 2rem; 
                border-radius: 12px;
                border: 1px solid #333;
            }
            .menu h1 { color: #1e3a8a; margin-bottom: 2rem; }
            .menu a { 
                display: inline-block; 
                margin: 1rem; 
                padding: 1rem 2rem; 
                background: #1e3a8a; 
                color: white; 
                text-decoration: none; 
                border-radius: 6px; 
                transition: all 0.3s ease;
            }
            .menu a:hover { 
                background: #1e40af; 
                transform: translateY(-2px);
            }
            .instructions {
                background: #1a1a1a;
                padding: 1.5rem;
                border-radius: 8px;
                margin-top: 2rem;
                border-left: 4px solid #1e3a8a;
            }
        </style>
    </head>
    <body>
        <div class="menu">
            <h1>🛠️ Error Templates Viewer</h1>
            <p>Click on any error type to see how it looks when rendered:</p>
            
            <div style="margin: 2rem 0;">
                <a href="/test/404">🔍 View 404 Error</a>
                <a href="/test/500">⚠️ View 500 Error</a>
                <a href="/test/403">🚫 View 403 Error</a>
            </div>
            
            <div class="instructions">
                <h3>📝 Instructions:</h3>
                <p>• Each link opens the error template with normal HTTP 200 status so you can see the design</p>
                <p>• Check how they look on different screen sizes</p>
                <p>• Test the navigation buttons to make sure they work</p>
                <p>• When done testing, remove this test route from your app</p>
            </div>
            
            <div style="margin-top: 2rem;">
                <a href="/" style="background: #333;">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''
