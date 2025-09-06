/*
LinkForge - Minimal Frontend for Backend Showcase
=================================================

Minimal JavaScript for essential form functionality only.
Focus remains on backend Python/Flask development.
*/

// Auto-hide flash messages
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

// Essential bulk operations
function selectAll() {
    const checkboxes = document.querySelectorAll('input[name="selected_links"]');
    const selectAllCheckbox = document.getElementById('select-all');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

console.log('🔗 LinkForge loaded - Backend-focused architecture!');
