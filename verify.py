"""
LinkForge Verification Script
============================

Run this script after extracting the ZIP to verify everything works.
"""

import os
import sys

def verify_project():
    """Verify the project structure and basic functionality."""

    print("🔍 Verifying LinkForge Project...")

    # Check required files
    required_files = [
        'app.py',
        'config.py', 
        'models.py',
        'requirements.txt',
        'blueprints/auth.py',
        'blueprints/links.py',
        'blueprints/main.py',
        'templates/base.html',
        'templates/dashboard.html',
        'static/style.css'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ All required files present")

    # Test imports
    try:
        import flask
        print("✅ Flask available")
    except ImportError:
        print("❌ Flask not installed. Run: pip install -r requirements.txt")
        return False

    try:
        import qrcode
        print("✅ QR code library available") 
    except ImportError:
        print("❌ QR code library not installed")
        return False

    # Test Jinja template syntax
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('templates'))

        # Test each template
        templates = ['base.html', 'landing.html', 'login.html', 'register.html', 'dashboard.html']
        for template_name in templates:
            template = env.get_template(template_name)
            print(f"✅ {template_name} syntax OK")

    except Exception as e:
        print(f"❌ Template syntax error: {e}")
        return False

    print("🎉 Project verification complete! Ready to run.")
    print("Run: python app.py")
    return True

if __name__ == '__main__':
    verify_project()
