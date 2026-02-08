function toggleFilters() {
    const panel = document.getElementById('filters-panel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleAllCheckboxes() {
    const checkboxes = document.querySelectorAll('.action-select');
    const toggle = document.getElementById('action-toggle');
    if (toggle) {
        checkboxes.forEach(cb => cb.checked = toggle.checked);
        updateCounter();
    }
}

function updateCounter() {
    const count = document.querySelectorAll('.action-select:checked').length;
    const counter = document.querySelector('.action-counter');
    if (counter) {
        counter.textContent = count + ' selected';
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.action-select').forEach(cb => {
        cb.addEventListener('change', updateCounter);
    });
});