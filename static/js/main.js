// ── Sidebar Toggle ──
document.getElementById('sidebarToggle')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('show');
});

// ── Live Clock ──
function updateClock() {
    const now = new Date();
    const options = { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    const el = document.getElementById('current-time');
    if (el) el.textContent = now.toLocaleDateString('en-US', options);
}
setInterval(updateClock, 1000);
updateClock();

// ── Toast Notification System ──
function showToast(title, message, type = 'info') {
    const icons = {
        success: 'bi-check-circle-fill text-success',
        error: 'bi-x-circle-fill text-danger',
        warning: 'bi-exclamation-triangle-fill text-warning',
        info: 'bi-info-circle-fill text-info',
    };
    const toastId = `toast-${Date.now()}`;
    const html = `
        <div id="${toastId}" class="toast border-0" role="alert"
             style="background: #1a1d26; border: 1px solid #2d3348 !important;">
            <div class="toast-header" style="background: transparent; border-bottom: 1px solid #2d3348;">
                <i class="bi ${icons[type] || icons.info} me-2"></i>
                <strong class="me-auto text-light">${title}</strong>
                <small class="text-muted">now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body text-light">${message}</div>
        </div>`;
    const container = document.getElementById('toastContainer');
    if (container) {
        container.insertAdjacentHTML('beforeend', html);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }
}

// ── API Helper ──
async function apiCall(url, method = 'GET', data = null) {
    try {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (data) options.body = JSON.stringify(data);
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('Error', `API call failed: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

// ── Loading State Helper ──
function setLoading(elementId, isLoading) {
    const el = document.getElementById(elementId);
    if (el) el.classList.toggle('d-none', !isLoading);
}
