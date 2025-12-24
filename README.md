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

6. **DOCKER**
     ```bash
   1. Заходим в настройки проекта на GitHub и выберавем *Secrets and variables*
   2. Добавляем новый секрет по кнопке *New repository secret* 
   3. на сервере созддаем новый ключ для GitHub ACTIONS:
   ssh-keygen -t ed25519 -C "github-actions@your-repo" -f github_actions_key
   и получите его из терминала
   cat github_actions_key.pub
   
   # Перезагрузите сессию или выполните:
   newgrp docker
   
7. ** Настройка CI/CD **
  
ЧАСТЬ 1. Подготовка удалённого сервера (Ubuntu 22.04)

    1. Установите необходимые компоненты

    Подключитесь к серверу по SSH и выполните:
         sudo apt update && sudo apt upgrade -y

    # Установка базовых утилит
        sudo apt install -y git curl wget build-essential libpq-dev python3-dev

    # Установка Docker и Docker Compose
        sudo apt install -y docker.io docker-compose
        sudo usermod -aG docker $USER  # Добавить текущего пользователя в группу docker
   
    2. Установите Poetry (опционально, но рекомендуется)
        curl -sSL https://install.python-poetry.org | python3 -
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        source ~/.bashrc
        poetry config virtualenvs.in-project true
   
    3. Создайте директорию проекта и перейдите в нее
   
       mkdir -p /home/test/Progect_Django_rest_HW
       cd /home/test/Progect_Django_rest_HW
   
    4. Настройте .env файл (если используется)
   
       Создайте файл .env в корне проекта с переменными окружения:
       nano .env
   
       Пример содержимого:
       SECRET_KEY=ваш_секретный_ключ
       DEBUG=False
       ALLOWED_HOSTS=ваш_домен_или_IP

       DB_NAME=postgres
       DB_USER=postgres
       DB_PASSWORD=postgres
       DB_HOST=db  # ← имя сервиса в docker-compose.yml
       DB_PORT=5432

      REDIS_HOST=redis
      REDIS_PORT=6379
   
    5. Подготовьте docker-compose.yml
    6. Подготовьте Dockerfile
   
ЧАСТЬ 2. Настройка GitHub Secrets
   
    В репозитории на GitHub:
    Перейдите в Settings → Secrets and variables → Actions
    Добавьте следующие секреты:
   
         НАЗВАНИЕ         ЗНАЧЕНИЕ
   
         SECRET_IP        IP-адрес вашего сервера (например, 192.168.1.10)
         SSH_USER         Имя пользователя на сервере (например, ubuntu)
         SSH_KEY          Приватный SSH-ключ (содержимое ~/.ssh/id_rsa или отдельного ключа)
   
    Рекомендуется создать отдельный SSH-ключ только для деплоя:
    ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -C "github-deploy"
    Публичный ключ (github_deploy.pub) добавьте в ~/.ssh/authorized_keys на сервере. 
   
ЧАСТЬ 3. Как запустить деплой
    
    1. Push в нужную ветку
       Workflow запускается автоматически при:
        а) git push в ветки: main, master, develop, feature/task8
        б) Открытии Pull Request в main, master, develop
              
    2. Этапы выполнения
     
        Lint: проверка кода (flake8 + black)
        Test: запуск тестов с PostgreSQL в контейнере
        Security: проверка уязвимостей через safety
        Deploy-SSH: если все прошло успешно — деплой на сервер
        
        ⚠️ Деплой выполняется только после успешного прохождения тестов (needs: test).
        
    3. Что делает шаг деплоя на сервере?
        Подключается по SSH
        Выполняет git pull в папке проекта
        Устанавливает зависимости через Poetry
        Применяет миграции
        Собирает статику
        Перезапускает контейнеры через docker compose up -d --build
        
    ✅ Проверка работы
        После успешного деплоя:

        **Демо:** Откройте в браузере: 
         http://your-server-ip:8000

        Проверьте логи контейнера:
        sudo docker compose logs web

 
## Лицензия 
   Этот проект распространяется по лицензии MIT.


5. **Документация:**
    ```bash
    API доступно по адресу:                   
    http://localhost:8000/swagger/#/

## Лицензия 
   Этот проект распространяется по лицензии MIT.

Контакты
📧 [grigoriy85@gmail.com](mailto:grigoriy85@gmail.com)
🔗 [Grigorii-Goncharov](https://github.com/Grigorii-Goncharov)