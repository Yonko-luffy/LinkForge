/*
LinkForge Complete - Minimal JavaScript
======================================

Essential functionality only. Focus remains on backend Python development.
Total lines: < 30 (as requested for minimal JavaScript complexity)
*/

// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(msg) {
        setTimeout(function() {
            msg.style.opacity = '0';
            setTimeout(function() {
                msg.remove();
            }, 300);
        }, 5000);
    });
});

// Simple form validation helper
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    for (let input of inputs) {
        if (!input.value.trim()) {
            input.focus();
            return false;
        }
    }
    return true;
}

// Utility function for any future enhancements
function showMessage(text, type = 'info') {
    const flash = document.createElement('div');
    flash.className = `flash-message flash-${type}`;
    flash.textContent = text;

    const container = document.querySelector('.flash-messages');
    if (container) {
        container.appendChild(flash);
        setTimeout(() => flash.remove(), 3000);
    }
}

console.log('🔗 LinkForge loaded - Backend-focused architecture ready!');
