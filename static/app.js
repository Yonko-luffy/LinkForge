// Check authentication status
async function checkAuth() {
    const res = await fetch('/api/user');
    const data = await res.json();
    
    if (data.username) {
        document.getElementById('user-info').innerHTML = `
            <span class="welcome-text">👋 Welcome back, <strong>${data.username}</strong>!</span>
            <button class="logout-btn" onclick="logout()">🚪 Logout</button>
        `;
        document.getElementById('user-section').style.display = 'flex';
        document.getElementById('main-app').style.display = 'block';
        document.getElementById('auth-required').style.display = 'none';
        loadHistory();
    } else {
        document.getElementById('user-section').style.display = 'none';
        document.getElementById('main-app').style.display = 'none';
        document.getElementById('auth-required').style.display = 'block';
    }
}

// Logout function
async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    checkAuth();
}

document.getElementById('shorten-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const longUrl = document.getElementById('long-url').value;
    
    // Show loading state
    const button = this.querySelector('button');
    const originalText = button.textContent;
    button.textContent = '🔨 Forging...';
    button.disabled = true;
    
    try {
        const res = await fetch('/shorten', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url: longUrl})
        });
        const data = await res.json();
        const resultDiv = document.getElementById('result');
        
        if (data.short_url) {
            resultDiv.innerHTML = `
                <div class="result-card">
                    <h3>⚡ Your link has been forged!</h3>
                    <p><strong>Forged URL:</strong> <a class='short-url' href='${data.short_url}' target='_blank'>${data.short_url}</a></p>
                    <p><strong>Original:</strong> ${longUrl}</p>
                    ${data.qr_code ? `
                        <div class='qr-section'>
                            <p><strong>📱 QR Code:</strong></p>
                            <img src='${data.qr_code}' alt='QR Code' width='180'>
                            <p><small>Scan this QR code to open the link on mobile</small></p>
                        </div>
                    ` : ''}
                </div>
            `;
            document.getElementById('long-url').value = '';
            loadHistory();
        } else {
            resultDiv.innerHTML = `
                <div class="result-card" style="border-left-color: #ff6b6b;">
                    <p style="color: #ff6b6b;">❌ ${data.error || 'Error forging link'}</p>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `
            <div class="result-card" style="border-left-color: #ff6b6b;">
                <p style="color: #ff6b6b;">❌ Network error. Please try again.</p>
            </div>
        `;
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
});

async function loadHistory() {
    const res = await fetch('/history');
    const data = await res.json();
    const historyDiv = document.getElementById('history');
    
    if (data.history && data.history.length) {
        let html = '<h2>� Your Forged Links</h2>';
        html += '<table><thead><tr><th>⚡ Forged URL</th><th>🌐 Original URL</th><th>📱 QR Code</th><th>📅 Created</th></tr></thead><tbody>';
        
        data.history.forEach(item => {
            const date = new Date(item.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            const shortUrl = item.short_url.length > 35 ? item.short_url.substring(0, 35) + '...' : item.short_url;
            const longUrl = item.long_url.length > 50 ? item.long_url.substring(0, 50) + '...' : item.long_url;
            
            html += `
                <tr>
                    <td><a href='${item.short_url}' target='_blank' title="${item.short_url}">${shortUrl}</a></td>
                    <td title="${item.long_url}">${longUrl}</td>
                    <td style="text-align: center;"><img src='${item.qr_code}' width='40' alt='QR' style="border-radius: 4px;"></td>
                    <td>${date}</td>
                </tr>
            `;
        });
        html += '</tbody></table>';
        historyDiv.innerHTML = html;
    } else {
        historyDiv.innerHTML = `
            <div class="empty-state">
                <h2>� Your Link Forge</h2>
                <p>⚡ No forged links yet. Create your first one above!</p>
            </div>
        `;
    }
}

// Initialize the app with smooth animations
window.onload = function() {
    checkAuth();
    
    // Add some interactive animations
    document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON') {
            // Create ripple effect
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255,255,255,0.3)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.pointerEvents = 'none';
            
            const rect = e.target.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            e.target.style.position = 'relative';
            e.target.style.overflow = 'hidden';
            e.target.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }
    });
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
};
