// static/js/main.js

// === ТЁМНАЯ ТЕМА ===
document.addEventListener('DOMContentLoaded', function () {
    const switchElement = document.getElementById('darkModeSwitch');

    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        if (switchElement) switchElement.checked = true;
    }

    if (switchElement) {
        switchElement.addEventListener('change', function () {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'enabled');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'disabled');
            }
        });
    }
});

// === ГЛОБАЛЬНЫЙ TOAST ===
function showToast(message, type = 'success', delay = 4000) {
    const bg = {
        success: 'bg-success',
        info: 'bg-info',
        danger: 'bg-danger',
        warning: 'bg-warning text-dark'
    }[type] || 'bg-success';

    const toastHtml = `
        <div class="toast align-items-center text-white ${bg} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    const container = document.getElementById('toastContainer');
    if (!container) return;

    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = container.lastElementChild;
    const toast = new bootstrap.Toast(toastEl, { delay });
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// === Показываем Django messages как тосты ===
document.addEventListener('DOMContentLoaded', function () {
    const el = document.getElementById('django-messages-data');
    if (!el) return;

    try {
        const messages = JSON.parse(el.textContent);
        messages.forEach(msg => {
            const type = msg.tags.includes('error') ? 'danger' :
                        msg.tags.includes('warning') ? 'warning' :
                        msg.tags.includes('info') ? 'info' : 'success';
            showToast(msg.message, type);
        });
    } catch (e) {
        console.error('Ошибка парсинга messages:', e);
    }
});

// === Обновление чек-листа на списке договоров ===
function handleChecklistChange(checkbox) {
    const form = checkbox.closest('form');
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'info', 2500);
        }
    })
    .catch(() => {
        showToast('Ошибка связи с сервером', 'danger');
        checkbox.checked = !checkbox.checked; // откатываем чекбокс
    });
}