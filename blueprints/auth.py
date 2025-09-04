"""
Authentication Blueprint - Clean Implementation
==============================================

User registration, login, and logout functionality.
Simple, secure, and fully working.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import create_user, authenticate_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with validation."""
    if 'user_id' in session:
        return redirect(url_for('links.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not all([username, email, password]):
            flash('All fields are required.', 'error')
            return render_template('register.html')

        result = create_user(username, email, password)

        if result['success']:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'error')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with session management."""
    if 'user_id' in session:
        return redirect(url_for('links.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        user = authenticate_user(username, password)

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True

            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('links.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """User logout with session cleanup."""
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('main.landing'))
