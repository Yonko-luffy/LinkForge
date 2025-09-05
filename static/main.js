// ========== STATIC QR CODE GENERATION ==========

// Generate QR codes for all links on the page
function generateAllStaticQRs() {
    const canvases = document.querySelectorAll('[id^="qr-static-"]');
    
    if (canvases.length === 0) return;
    
    canvases.forEach(canvas => {
        const linkId = canvas.id.replace('qr-static-', '');
        generateStaticQR(linkId);
    });
}

// Generate a single static QR code
function generateStaticQR(linkId) {
    const canvas = document.getElementById('qr-static-' + linkId);
    if (!canvas) return;
    
    // Get URL from data attribute
    const dataUrl = canvas.getAttribute('data-url');
    if (dataUrl) {
        generateQRFromUrl(canvas, dataUrl, linkId);
        return;
    }
    
    // Fallback to finding URL from DOM
    const linkRow = canvas.closest('.link-item');
    if (!linkRow) {
        const fallbackUrl = window.location.origin + '/test' + linkId;
        generateQRFromUrl(canvas, fallbackUrl, linkId);
        return;
    }
    
    const visitLink = linkRow.querySelector('a[href^="/"]');
    if (!visitLink) {
        const fallbackUrl = window.location.origin + '/link' + linkId;
        generateQRFromUrl(canvas, fallbackUrl, linkId);
        return;
    }
    
    const shortCode = visitLink.getAttribute('href').substring(1);
    const fullUrl = window.location.origin + '/' + shortCode;
    generateQRFromUrl(canvas, fullUrl, linkId);
}

// Generate QR from a given URL
function generateQRFromUrl(canvas, url, linkId) {
    // Check if qrcode library is available
    if (typeof qrcode === 'undefined') {
        generateFallbackQR(canvas, url, linkId);
        return;
    }
    
    try {
        // Create QR code
        const qr = qrcode(0, 'M');
        qr.addData(url);
        qr.make();
        
        const moduleCount = qr.getModuleCount();
        const cellSize = Math.floor(120 / moduleCount);
        const qrSize = cellSize * moduleCount;
        
        canvas.width = qrSize;
        canvas.height = qrSize;
        
        const ctx = canvas.getContext('2d');
        
        // White background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, qrSize, qrSize);
        
        // Black QR pattern
        ctx.fillStyle = '#000000';
        for (let row = 0; row < moduleCount; row++) {
            for (let col = 0; col < moduleCount; col++) {
                if (qr.isDark(row, col)) {
                    ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
                }
            }
        }
    } catch (error) {
        generateFallbackQR(canvas, url, linkId);
    }
}

// Fallback QR generation - switch to server-generated image
function generateFallbackQR(canvas, url, linkId) {
    const img = document.getElementById('qr-image-' + linkId);
    if (img) {
        canvas.style.display = 'none';
        img.style.display = 'block';
        img.onerror = function() {
            showQRPlaceholder(canvas, url, linkId);
        };
        return;
    }
    
    showQRPlaceholder(canvas, url, linkId);
}

function showQRPlaceholder(canvas, url, linkId) {
    canvas.width = 120;
    canvas.height = 120;
    const ctx = canvas.getContext('2d');
    
    // White background with border
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 120, 120);
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.strokeRect(5, 5, 110, 110);
    
    // Text content
    ctx.fillStyle = '#000000';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    
    const shortCode = url.split('/').pop();
    ctx.fillText('QR Code', 60, 30);
    ctx.fillText('for:', 60, 45);
    ctx.fillText(shortCode || 'link', 60, 65);
    ctx.fillText('(Click Download)', 60, 85);
    ctx.fillText('for actual QR', 60, 100);
}

// Show error state on canvas
function showErrorOnCanvas(canvas, message) {
    canvas.width = 120;
    canvas.height = 120;
    const ctx = canvas.getContext('2d');
    
    // Dark gray background
    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, 120, 120);
    
    // White text
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('QR Error', 60, 50);
    ctx.fillText(message, 60, 70);
}

// ========== END STATIC QR GENERATION ==========

// Edit link functionality
function editLink(linkId) {
    document.getElementById('link-' + linkId).style.display = 'none';
    document.getElementById('edit-' + linkId).style.display = 'flex';
}

function cancelEdit(linkId) {
    document.getElementById('edit-' + linkId).style.display = 'none';
    document.getElementById('link-' + linkId).style.display = 'flex';
}

function toggleLinkStatus(linkId) {
    fetch('/toggle_status/' + linkId, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while toggling link status.');
    });
}

function deleteLink(linkId) {
    if (confirm('Are you sure you want to delete this link? This action cannot be undone.')) {
        fetch('/delete_link/' + linkId, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the link.');
        });
    }
}

// Bulk operations
function bulkToggleStatus() {
    const checkboxes = document.querySelectorAll('input[name="selected_links"]:checked');
    const linkIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (linkIds.length === 0) {
        alert('Please select at least one link.');
        return;
    }

    fetch('/bulk_toggle_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({link_ids: linkIds})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during bulk operation.');
    });
}

function bulkDelete() {
    const checkboxes = document.querySelectorAll('input[name="selected_links"]:checked');
    const linkIds = Array.from(checkboxes).map(cb => cb.value);
    
    if (linkIds.length === 0) {
        alert('Please select at least one link.');
        return;
    }

    if (confirm(`Are you sure you want to delete ${linkIds.length} link(s)? This action cannot be undone.`)) {
        fetch('/bulk_delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({link_ids: linkIds})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during bulk deletion.');
        });
    }
}

function selectAll() {
    const checkboxes = document.querySelectorAll('input[name="selected_links"]');
    const selectAllCheckbox = document.getElementById('select-all');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}
