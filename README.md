# Проект ТРЕКЕР ПРИВЫЧЕК на Django REST API
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

## Использование

1. **Запустите сервер разработки:**
   ```bash
   python manage.py runserver

2. **Запустите celery для ОС WINDOWS:**
   ```bash
   poetry run celery -A config worker -l INFO --pool=solo
   poetry run celery -A config worker -l INFO

3. **Основные возможности API:**
    ```bash
    Регистрация пользователя:
    http://localhost:8000/users/register/ - post(json-raw)

    Вход пользователем и получение токена post:
    http://localhost:8000/users/login/ в body отправить json (json-raw)

    Просмотр профиля get:
    http://localhost:8000/users/profile/ (headers) Accept - Bearer your_tocken

    Редактирование профиля patch:
    http://localhost:8000/users/profile/ (json-raw) patch + (headers) Accept -Bearer your_tocken (ТОЛЬКО ВЛАДЕЛЬЦАМ)

    Редактирование профиля полностью( нужны важные поля входа в аккаунт) put:
    http://localhost:8000/users/profile/ (json-raw) patch + (headers) Accept - Bearer your_tocken (ТОЛЬКО ВЛАДЕЛЬЦАМ)

    Удаление профиля delete:
    http://localhost:8000/users/profile/delete (headers) Bearer your_tocken (ТОЛЬКО ВЛАДЕЛЬЦАМ)

    Просмотр списков пользователя get:
    http://localhost:8000/users/list/(headers) Accept - Bearer your_tocken (ТОЛЬКО АДМИНАМ)
   
    Главная страница:
    http://localhost:8000/htracker/
   
    Просмотр привычки по ID:
    http://localhost:8000/htracker/7/(headers) Accept - Bearer your_tocken
   
    Пример запроса на сортировку по времени: 
    http://localhost:8000/htracker/?ordering=time

4. **Тестирование:** 
   ```bash
     Запустите команду:                       coverage run --source='htracker' manage.py test htracker.tests
     Создайте отчет, запустите команду:       coverage report
     Отчет HTML, запустите команду:           coverage html
   
   Отчет тестов создастся по пути *HabitTracker\htmlcov\index.html*

5. **Документация:**
    ```bash
    API доступно по адресу:                   
    http://localhost:8000/swagger/#/

## Лицензия 
   Этот проект распространяется по лицензии MIT.

Контакты
📧 [grigoriy85@gmail.com](mailto:grigoriy85@gmail.com)
🔗 [Grigorii-Goncharov](https://github.com/Grigorii-Goncharov)