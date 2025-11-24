// static/js/main.js

// === ТЁМНАЯ ТЕМА ===
document.addEventListener('DOMContentLoaded', function () {
    const switchElement = document.getElementById('darkModeSwitch');

    // Восстанавливаем сохранённую тему
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        if (switchElement) switchElement.checked = true;
    }

    // Переключатель темы
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
function showToast(message, type = 'success') {
    const bg = type === 'success' ? 'bg-success' : 'bg-danger';
    const icon = type === 'success' ? 'Success' : 'Error';
    const toastHtml = `
        <div class="toast align-items-center text-white ${bg} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body"><strong>${icon}</strong> ${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>`;

    const container = document.getElementById('toast-container');
    if (container) {
        container.insertAdjacentHTML('beforeend', toastHtml);
        new bootstrap.Toast(container.lastElementChild, { delay: 3000 }).show();
    }
}

// === Обновление чек-листа на списке договоров ===
function handleChecklistChange(checkbox) {
    const form = checkbox.form;
    const formData = new FormData(form);
    formData.set(checkbox.name, checkbox.checked);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(() => {
        showToast('Чек-лист обновлён', 'success');
        const card = form.closest('.contract-card');
        card.style.background = '#d4edda';
        card.style.transition = 'background 0.4s';
        setTimeout(() => card.style.background = '', 600);
    })
    .catch(() => {
        showToast('Ошибка сохранения', 'danger');
        checkbox.checked = !checkbox.checked;
    });
}