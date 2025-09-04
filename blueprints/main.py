"""
Main Blueprint - Landing and Static Pages
=========================================

Landing page and general application routes.
"""

from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    """Enhanced landing page with detailed information."""
    if 'user_id' in session:
        return redirect(url_for('links.dashboard'))

    return render_template('landing.html')

@main_bp.route('/features')
def features():
    """Features page with detailed explanations."""
    return render_template('features.html')

@main_bp.route('/health')
def health():
    """Health check for deployment platforms."""
    return {'status': 'healthy', 'app': 'LinkForge Dynamic'}
