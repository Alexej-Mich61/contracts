# Техническое обслуживание — Долгосрочные договоры

![Django](https://img.shields.io/badge/Django-5.1-092e20?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Private-red)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)

Полноценная корпоративная система учёта долгосрочных договоров технического обслуживания с абонентскими комплектами (
АК).

## Возможности

- Создание, редактирование, удаление договоров
- Прикрепление до 3 файлов к договору
- Умный чек-лист (Госуслуги / ОКО / Сполох)
- Множественный выбор работ
- Автоматический статус: Ожидание → Действует → Завершён
- Полнотекстовый поиск по заказчику и ИНН
- Фильтры: статус, исполнитель, район, адрес АК, чек-лист, работы
- Сортировка: по дате создания, по алфавиту
- Пагинация + счётчики (договоров / АК)
- Экспорт в Excel с текущими фильтрами
- Роли: Administrators (полный доступ) и Viewers (только просмотр)
- Идеальная тёмная тема (как в GitHub)
- Адаптивный интерфейс (мобильные + планшеты)
- Фавикон + PWA-ready
- Безопасное хранение файлов по годам: `media/contracts/files/2026/...`

## Технологии

- Django 5.1
- Bootstrap 5 + crispy-forms
- SQLite (локально) → легко мигрируется на PostgreSQL
- argon2-cffi (безопасное хэширование паролей на Linux)
- Black + isort + pre-commit
- pip-tools (requirements.in / requirements-dev.in)

## Скриншоты

![Главная страница (тёмная тема)](screenshots/main_dark.png)
![Детали договора](screenshots/detail.png)
![Экспорт в Excel · Тосты · Адаптивность

## Локальный запуск

```bash
# 1. Клонируем
git clone https://github.com/твой-ник/contracts-new.git
cd contracts-new

# 2. Создаём виртуальное окружение
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Устанавливаем зависимости
pip install -r requirements-dev.txt

# 4. Применяем миграции
python manage.py migrate

# 5. Создаём суперпользователя
python manage.py createsuperuser

# 6. Запускаем
python manage.py runserver
