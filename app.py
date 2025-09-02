from flask import Flask, request, redirect, jsonify, render_template, session
import sqlite3
import string
import random
import qrcode
import io
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database setup
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY, user_id INTEGER, long_url TEXT, short_code TEXT UNIQUE, 
                  created_at TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

# Helper to generate a short code
def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# Generate QR code
def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                  (username, password_hash))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['username'] = username
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/shorten', methods=['POST'])
def shorten_url():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    data = request.get_json()
    long_url = data.get('url')
    if not long_url:
        return jsonify({'error': 'No URL provided'}), 400
    
    # Add protocol if missing
    if not long_url.startswith(('http://', 'https://')):
        long_url = 'https://' + long_url
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    # Generate unique short code
    code = generate_code()
    while True:
        c.execute('SELECT id FROM urls WHERE short_code = ?', (code,))
        if not c.fetchone():
            break
        code = generate_code()
    
    # Save to database
    c.execute('INSERT INTO urls (user_id, long_url, short_code, created_at) VALUES (?, ?, ?, ?)',
              (session['user_id'], long_url, code, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    short_url = request.host_url + code
    qr_code = generate_qr_code(short_url)
    
    return jsonify({
        'short_url': short_url,
        'qr_code': qr_code
    })

@app.route('/history')
def get_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT long_url, short_code, created_at FROM urls WHERE user_id = ? ORDER BY created_at DESC',
              (session['user_id'],))
    urls = c.fetchall()
    conn.close()
    
    history = []
    for url in urls:
        short_url = request.host_url + url[1]
        qr_code = generate_qr_code(short_url)
        history.append({
            'long_url': url[0],
            'short_url': short_url,
            'qr_code': qr_code,
            'created_at': url[2]
        })
    
    return jsonify({'history': history})

@app.route('/api/user')
def get_user():
    if 'user_id' in session:
        return jsonify({'username': session['username']})
    return jsonify({'username': None})

@app.route('/<code>')
def redirect_url(code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT long_url FROM urls WHERE short_code = ?', (code,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return redirect(result[0])
    return jsonify({'error': 'URL not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
