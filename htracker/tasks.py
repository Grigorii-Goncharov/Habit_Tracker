from celery import shared_task

from htracker.models import Habit
from users.services import send_telegram_message


#Bind - создает экземпляр задачи(для работы с повторами)
@shared_task(bind=True, max_retries=3)
#self -обязателен, если используешь bind(без него не работает self.retry)
def send_telegram_reminder(self, chat_id, message):
    """Отправление напоминаний в телеграмм"""

    try:
        send_telegram_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка отправки Telegram: {e}")
        raise self.retry(exception=e, countdown=60)  # повтор через 60 сек


@shared_task
def check_status(habit_id):
    """Функция смены статуса на /провалено/ """
    try:
        habit = Habit.objects.get(id=habit_id)
        if habit.status == "started":
            habit.status = "failed"
            habit.save()
            # Отправить уведомление
            if habit.owner.telegram_chat_id:
                message = f"Время на выполнение привычки '{habit.action}' истекло. Привычка помечена как проваленная."
                send_telegram_message(habit.owner.telegram_chat_id, message)
    except Habit.DoesNotExist:
        pass  # Привычка удалена — игнорируем
