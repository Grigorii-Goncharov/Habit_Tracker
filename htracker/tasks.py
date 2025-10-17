from celery import shared_task
from django.utils import timezone
from htracker.models import Habit
from users.services import send_telegram_message


@shared_task(bind=True, max_retries=3)
def send_telegram_message_task(self, chat_id, message):
    """Надёжная отправка с повторами"""
    try:
        send_telegram_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка отправки Telegram: {e}")
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_reminder(habit_id):
    """Напоминание по периодичности"""
    try:
        habit = Habit.objects.get(id=habit_id)
        if habit.owner.telegram_chat_id:
            message = f"Напоминание: пора выполнить привычку '{habit.action}'!"
            send_telegram_message_task.delay(habit.owner.telegram_chat_id, message)
    except Habit.DoesNotExist:
        pass


@shared_task
def send_failure(habit_id):
    """Проваленная задача из-за отсутствия выполнения 7 дней"""
    try:
        habit = Habit.objects.get(id=habit_id)
        if habit.owner.telegram_chat_id:
            message = f"Привычка '{habit.action}' провалена: не выполнена 7 дней."
            send_telegram_message_task.delay(habit.owner.telegram_chat_id, message)
        habit.status = 'failed'
        habit.save(update_fields=['status'])
    except Habit.DoesNotExist:
        pass


@shared_task
def check_all_habits():
    """Основная фоновая проверка (запускать через Celery Beat)"""
    now = timezone.now()
    for habit in Habit.objects.filter(status='started'):
        last_time = habit.last_completed_at or habit.created_at
        days_passed = (now - last_time).days

        # Напоминание по периодичности
        if days_passed >= habit.periodicity:
            send_reminder.delay(habit.id)

        # Проваленная задача через 7 дней
        if days_passed >= 7:
            send_failure.delay(habit.id)

