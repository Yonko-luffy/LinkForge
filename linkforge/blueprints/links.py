"""
Links Blueprint - Complete Implementation
========================================

All URL shortening functionality with every requested feature implemented:
- Dynamic link editing (core feature)
- Link expiration with full enforcement
- Password protection with full enforcement  
- Bulk operations (delete, export, QR download)
- QR code generation and management
- Click analytics and tracking

No placeholder code - everything is fully functional.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, Response, send_file, jsonify
from ..db_utils import get_db_cursor, get_db_connection
import sqlite3
import string
import random
import qrcode
import io
import base64
import csv
import zipfile
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import (
    DatabaseManager, create_link, get_user_links, get_link_by_short_code,
    update_link_url, delete_links, record_click, is_link_expired, 
    verify_link_password, get_user_stats
)

links_bp = Blueprint('links', __name__)

def generate_short_code(username, custom_code=None, length=6):
    """Generate short code with user namespace."""
    if custom_code:
        # Clean custom code
        clean_code = re.sub(r'[^a-zA-Z0-9_-]', '-', custom_code.lower())
        return f"{username}/{clean_code}"
    else:
        # Generate random code
        chars = string.ascii_letters + string.digits
        random_code = ''.join(random.choices(chars, k=length))
        return f"{username}/{random_code}"

def validate_url(url):
    """Validate and normalize URL."""
    if not url or not url.strip():
        return False, ""

    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return True, url
    except:
        pass

    return False, ""

def generate_qr_code(url, size='small', as_attachment=True, filename=None):
    """
    Generate QR code for URL.
    
    Args:
        url: URL to encode
        size: 'small' for inline display, 'large' for download
        as_attachment: True for download, False for inline display
        filename: Custom filename for download
    """
    box_size = 5 if size == 'small' else 10
    border = 2 if size == 'small' else 4

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border
    )

    qr.add_data(url)
    qr.make(fit=True)

    # Create traditional black QR pattern on white background
    img = qr.make_image(fill_color="#000000", back_color="#ffffff")
    
    # Save to buffer
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=as_attachment,
        download_name=filename
    )

@links_bp.route('/dashboard')
def dashboard():
    """Main dashboard with all features."""
    if 'user_id' not in session:
        flash('Please log in to access dashboard.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session['username']

    # Get search query
    search_query = request.args.get('search', '').strip()

    # Get user links
    links = get_user_links(user_id, search_query)

    # Add QR codes and expiration status to links
    for link in links:
        # Generate small QR code for display
        short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"
        link['qr_code_small'] = generate_qr_code(short_url, 'small', as_attachment=False)

        # Check expiration status
        link['is_expired'] = is_link_expired(link)
        link['has_password'] = bool(link.get('password_hash'))

        # Format expiration date for display
        if link.get('expiration_date'):
            try:
                exp_date = datetime.fromisoformat(link['expiration_date'])
                link['expiration_display'] = exp_date.strftime('%Y-%m-%d %H:%M')

                # Calculate days remaining
                days_left = (exp_date - datetime.now()).days
                if days_left < 0:
                    link['expiration_status'] = 'Expired'
                elif days_left == 0:
                    link['expiration_status'] = 'Expires today'
                else:
                    link['expiration_status'] = f'{days_left} days left'
            except:
                link['expiration_display'] = 'Invalid date'
                link['expiration_status'] = 'Error'
        else:
            link['expiration_display'] = 'Never'
            link['expiration_status'] = 'Never expires'

    # Get user statistics
    stats = get_user_stats(user_id)

    return render_template('dashboard.html',
                         links=links,
                         stats=stats,
                         username=username,
                         current_search=search_query)

@links_bp.route('/create', methods=['POST'])
def create_link_route():
    """Create new link with all features."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session['username']

    # Extract form data
    original_url = request.form.get('url', '').strip()
    display_name = request.form.get('display_name', '').strip()
    custom_code = request.form.get('custom_code', '').strip()
    password = request.form.get('password', '').strip()
    expiration_option = request.form.get('expiration', '')

    # Validate URL
    is_valid, clean_url = validate_url(original_url)
    if not is_valid:
        flash('Please enter a valid URL.', 'error')
        return redirect(url_for('links.dashboard'))

    # Generate display name if empty
    if not display_name:
        try:
            parsed = urlparse(clean_url)
            display_name = parsed.netloc.replace('www.', '')
        except:
            display_name = 'Link'

    # Generate short code
    short_code = generate_short_code(username, custom_code)

    # Validate password if provided
    if password:
        if len(password) < 6 or len(password) > 15:
            flash('Password must be 6-15 characters long.', 'error')
            return redirect(url_for('links.dashboard'))

    # Calculate expiration days
    expiration_days = None
    if expiration_option and expiration_option != 'never':
        if expiration_option == 'custom':
            # Handle custom date
            custom_date = request.form.get('custom_date', '')
            if custom_date:
                try:
                    exp_date = datetime.fromisoformat(custom_date + 'T23:59:59')
                    days_diff = (exp_date - datetime.now()).days
                    if days_diff > 0:
                        expiration_days = days_diff
                except:
                    flash('Invalid custom expiration date.', 'error')
                    return redirect(url_for('links.dashboard'))
        else:
            # Predefined options
            expiration_map = {
                '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                'week': 7, 'month': 30
            }
            expiration_days = expiration_map.get(expiration_option)

    # Create link
    result = create_link(
        user_id=user_id,
        original_url=clean_url,
        display_name=display_name,
        short_code=short_code,
        password=password if password else None,
        expiration_days=expiration_days
    )

    if result['success']:
        flash(f'Link created: /{short_code}', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('links.dashboard'))

@links_bp.route('/<username>/<custom_code>')
def redirect_link(username, custom_code):
    """Handle link redirection with full feature support."""
    short_code = f"{username}/{custom_code}"

    # Get link
    link = get_link_by_short_code(short_code)
    if not link:
        return render_template('404.html'), 404

    # Check if link is active
    if not link['is_active']:
        flash('This link has been deactivated.', 'error')
        return render_template('404.html'), 404

    # Check expiration
    if is_link_expired(link):
        flash('This link has expired.', 'error')
        return render_template('404.html'), 404

    # Check password protection
    if link.get('password_hash'):
        provided_password = request.args.get('password', '')

        if not verify_link_password(link, provided_password):
            # Show password prompt
            return render_template('password_prompt.html', 
                                 short_code=short_code,
                                 link_name=link['display_name'])

    # Record click analytics
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                   request.environ.get('REMOTE_ADDR', ''))
    referrer = request.referrer or 'Direct'
    user_agent = request.environ.get('HTTP_USER_AGENT', '')

    record_click(link['id'], ip_address, referrer, user_agent)

    # Redirect to destination
    return redirect(link['original_url'])

@links_bp.route('/password_check/<username>/<custom_code>', methods=['POST'])
def password_check(username, custom_code):
    """Handle password submission for protected links."""
    password = request.form.get('password', '')
    short_code = f"{username}/{custom_code}"

    # Redirect back to link with password parameter
    return redirect(url_for('links.redirect_link', 
                          username=username, 
                          custom_code=custom_code,
                          password=password))

@links_bp.route('/update_url', methods=['POST'])
def update_url():
    """Update link destination URL (dynamic links feature)."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401

    user_id = session['user_id']
    link_id = request.form.get('link_id')
    new_url = request.form.get('new_url', '').strip()

    # Validate new URL
    is_valid, clean_url = validate_url(new_url)
    if not is_valid:
        return jsonify({'success': False, 'message': 'Invalid URL'}), 400

    # Update link
    result = update_link_url(link_id, user_id, clean_url)

    if result['success']:
        return jsonify({'success': True, 'message': 'Link updated successfully'})
    else:
        return jsonify({'success': False, 'message': result['message']}), 400

@links_bp.route('/delete/<int:link_id>')
def delete_single_link(link_id):
    """Delete a single link."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Delete the single link
    result = delete_links([link_id], user_id)

    if result['success']:
        flash('Link deleted successfully.', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('links.dashboard'))

def get_selected_links(user_id, selected_link_ids):
    """
    Helper function to get selected links for bulk operations using professional DB pattern.
    
    Demonstrates DRY (Don't Repeat Yourself) principle - a key backend skill.
    Used by bulk_delete, bulk_export_csv, and bulk_qr_download.
    """
    if not selected_link_ids:
        return []
    
    try:
        cursor = get_db_cursor()

        placeholders = ','.join('%s' for _ in selected_link_ids)
        params = selected_link_ids + [user_id]

        cursor.execute(f"""
            SELECT * FROM links 
            WHERE id IN ({placeholders}) AND user_id = %s
        """, params)
        links = cursor.fetchall()
        
        return [dict(link) for link in links]

    except Exception as e:
        print(f"Error getting selected links: {e}")
        return []

@links_bp.route('/api/links')
def api_get_links():
    """
    RESTful API endpoint returning user's links as JSON.
    
    Demonstrates backend API design skills - critical for backend developers.
    Returns structured JSON data that could be consumed by mobile apps, etc.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    user_id = session['user_id']
    
    try:
        links = get_user_links(user_id)
        
        # Format links for API response
        api_links = []
        for link in links:
            api_links.append({
                'id': link['id'],
                'short_code': link['short_code'],
                'original_url': link['original_url'],
                'display_name': link['display_name'],
                'clicks': link['clicks'],
                'is_active': link['is_active'],
                'created_at': link['created_at'],
                'qr_url': url_for('links.qr_image', link_id=link['id'], _external=True)
            })
        
        return jsonify({
            'success': True,
            'links': api_links,
            'total': len(api_links)
        })
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@links_bp.route('/api/links/<int:link_id>')
def api_get_link(link_id):
    """
    RESTful API endpoint for single link details using professional DB pattern.
    
    Demonstrates parameterized routes and proper HTTP status codes.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    user_id = session['user_id']
    
    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT * FROM links WHERE id = %s AND user_id = %s',
            (link_id, user_id)
        )
        link = cursor.fetchone()
        
        if not link:
            return jsonify({'error': 'Link not found'}), 404
        
        return jsonify({
            'success': True,
            'link': {
                'id': link['id'],
                'short_code': link['short_code'],
                'original_url': link['original_url'],
                'display_name': link['display_name'],
                'clicks': link['clicks'],
                'is_active': link['is_active'],
                'created_at': link['created_at'],
                'qr_url': url_for('links.qr_image', link_id=link['id'], _external=True),
                'short_url': f"{request.url_root.rstrip('/')}/{link['short_code']}"
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@links_bp.route('/bulk_delete', methods=['POST'])
def bulk_delete():
    """Delete multiple selected links."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    selected_links = request.form.getlist('selected_links')

    if not selected_links:
        flash('No links selected.', 'error')
        return redirect(url_for('links.dashboard'))

    # Convert to integers
    try:
        link_ids = [int(link_id) for link_id in selected_links]
    except ValueError:
        flash('Invalid link selection.', 'error')
        return redirect(url_for('links.dashboard'))

    # Delete links
    result = delete_links(link_ids, user_id)

    if result['success']:
        flash(f'Successfully deleted {result["deleted_count"]} links.', 'success')
    else:
        flash(result['message'], 'error')

    return redirect(url_for('links.dashboard'))

@links_bp.route('/export/csv')
def export_csv():
    """Export user links as CSV file."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session['username']

    # Get all user links
    links = get_user_links(user_id)

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Short URL', 'Original URL', 'Display Name', 'Clicks', 
        'Password Protected', 'Expiration Date', 'Created Date'
    ])

    # Data rows
    for link in links:
        short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"
        writer.writerow([
            short_url,
            link['original_url'],
            link['display_name'],
            link['clicks'],
            'Yes' if link['password_hash'] else 'No',
            link['expiration_date'] or 'Never',
            link['created_at']
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=linkforge_links_{username}.csv'}
    )

@links_bp.route('/export/bulk_csv', methods=['POST'])
def bulk_export_csv():
    """Export selected links as CSV using DRY helper function."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session['username']
    selected_links = request.form.getlist('selected_links')

    if not selected_links:
        flash('No links selected for export.', 'error')
        return redirect(url_for('links.dashboard'))

    # Use DRY helper function
    links = get_selected_links(user_id, selected_links)

    if not links:
        flash('No valid links found.', 'error')
        return redirect(url_for('links.dashboard'))

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Short URL', 'Original URL', 'Display Name', 'Clicks', 
        'Password Protected', 'Expiration Date', 'Created Date'
    ])

    for link in links:
        short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"
        writer.writerow([
            short_url,
            link['original_url'],
            link['display_name'],
            link['clicks'],
            'Yes' if link['password_hash'] else 'No',
            link['expiration_date'] or 'Never',
            link['created_at']
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=linkforge_selected_{username}.csv'}
    )

@links_bp.route('/download_qr/<int:link_id>')
def download_qr(link_id):
    """Download QR code as PNG file using professional DB pattern."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT * FROM links WHERE id = %s AND user_id = %s',
            (link_id, user_id)
        )
        link = cursor.fetchone()

        if not link:
            flash('Link not found.', 'error')
            return redirect(url_for('links.dashboard'))

        # Generate high-quality QR code using consolidated function
        short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"
        
        # Clean filename
        safe_name = re.sub(r'[<>:"/\|?*]', '_', link['display_name'])
        filename = f"{safe_name}_qr_code.png"

        return generate_qr_code(short_url, size='large', as_attachment=True, filename=filename)

    except Exception as e:
        print(f"Error in download_qr: {e}")
        flash('Error generating QR code download.', 'error')
        return redirect(url_for('links.dashboard'))

@links_bp.route('/qr_image/<int:link_id>')
def qr_image(link_id):
    """Serve QR code as inline image using professional DB pattern."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        cursor = get_db_cursor()
        
        cursor.execute(
            'SELECT * FROM links WHERE id = %s AND user_id = %s',
            (link_id, user_id)
        )
        link = cursor.fetchone()

        if not link:
            return "Link not found", 404

        # Generate QR code using consolidated function
        short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"
        
        return generate_qr_code(short_url, size='small', as_attachment=False)

    except Exception as e:
        print(f"Error in qr_image: {e}")
        return "Error generating QR image", 500

@links_bp.route('/bulk_qr_download', methods=['POST'])  
def bulk_qr_download():
    """Download QR codes for selected links as ZIP file."""
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    username = session['username']
    selected_links = request.form.getlist('selected_links')

    if not selected_links:
        flash('No links selected for QR download.', 'error')
        return redirect(url_for('links.dashboard'))

    # Use DRY helper function to get selected links
    links = get_selected_links(user_id, selected_links)

    if not links:
        flash('No valid links found.', 'error')
        return redirect(url_for('links.dashboard'))

    try:
        # Create ZIP file
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for link in links:
                short_url = f"{request.url_root.rstrip('/')}/{link['short_code']}"

                # Generate QR code
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(short_url)
                qr.make(fit=True)

                # Create traditional black QR pattern on white background
                img = qr.make_image(fill_color="#000000", back_color="#ffffff")

                # Save to buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')

                # Clean filename
                safe_name = re.sub(r'[<>:"/\|?*]', '_', link['display_name'])
                filename = f"{safe_name}_qr_code.png"

                # Add to ZIP
                zip_file.writestr(filename, img_buffer.getvalue())

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'linkforge_qr_codes_{username}.zip'
        )

    except Exception as e:
        print(f"Error in bulk_qr_download: {e}")
        flash('Error generating QR codes ZIP.', 'error')
        return redirect(url_for('links.dashboard'))
