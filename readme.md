# Проект Django REST API (Домашнее задание)

    Habit_Tracker бэкенд-часть SPA веб-приложения.

## Описание
    бэкенд-часть SPA веб-приложения.
    Habit Tracker

**Основные функции:**
    Управление курсами и уроками: создание, редактирование, удаление.
    Платежная система: оплата курсов и уроков через Stripe.
    Подписки: пользователи могут подписываться на курсы и получать уведомления об обновлениях.
    Гибкие права доступа:
        - Пользователи: могут создавать свои курсы/уроки, оплачивать контент, управлять подписками.
        - Модераторы: могут просматривать и редактировать все курсы/уроки, но не удалять их.
        - Администраторы: полный доступ ко всем функциям.
    REST API: полный набор эндпоинтов для интеграции с фронтендом или мобильными приложениями.
J   WT-аутентификация: безопасный вход и управление сессиями.

## Установка
    **Требования:**
        - Python 3.9+
        - PostgreSQL (или другая СУБД, поддерживаемая Django)
         - Stripe аккаунт (для тестовых платежей)

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Grigorii-Goncharov/Habit_Tracker.git
   cd Habit_Tracker
   
2. **Создайте и активируйте виртуальное окружение**
   ```bash
    python -m venv venv
    source venv/bin/activate        # Linux/macOS
    venv\Scripts\activate           # Windows
    
3. **Установите зависимости:**
    ```bash
   pip install -r requirements.txt

4. **Настройте переменные окружения**
    ```bash
    SECRET_KEY=your_SECRET_KEY

    DEBUG=your_DEBUG

    DB_NAME=your_db_name
    DB_USER=your_db_user_name
    DB_PASSWORD=your_PASSWORD
    DB_HOST=your_host
    DB_PORT=your_port

    MAIL_HOST=your_app_mail
    MAIL_PASSWORD=your_app_PASSWORD

    STRIPE_SECRET_KEY=your_STRIPE_SECRET_KEY

## Использование
1. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver
**Запустите celery для ОС WINDOWS:**
   poetry run celery -A config worker -l INFO --pool=solo
   poetry run celery -A config worker -l INFO
   
2. **API доступно по адресу:**
    http://127.0.0.1:8000/api/redoc
    http://127.0.0.1:8000/swagger/#/
 
3. **Основные возможности API:**
    ```bash
   
    ОПИСАНИЕ

4. **Авторизация:** 
   ```bash
   ОПИСАНИЕ

5. **Технические особенности:** 
   ```bash
    ОПИСАНИЕ

## Лицензия 
   Этот проект распространяется по лицензии MIT.

Контакты
📧 [grigoriy85@gmail.com](mailto:grigoriy85@gmail.com)
🔗 [Grigorii-Goncharov](https://github.com/Grigorii-Goncharov)