from celery import shared_task
from .services import send_telegram_message

#Bind - создает экземпляр задачи(для работы с повторами)
@shared_task(bind=True, max_retries=3)
#self -обязателен, если используешь bind(без него не работает self.retry)
def send_welcome_telegram(self, chat_id):
    try:
        send_telegram_message(chat_id, "🎉 Добро пожаловать!")
    except Exception as e:
        print(f"Ошибка отправки Telegram: {e}")
        raise self.retry(exception=e, countdown=60)  # повтор через 60 сек
