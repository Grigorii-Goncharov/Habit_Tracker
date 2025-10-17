from datetime import time, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from htracker.models import Habit
from htracker.tasks import (check_all_habits, send_failure, send_reminder,
                            send_telegram_message_task)
from users.models import User


#  Временно изменяет настройки Django только для тестов (отправить синхронно вместо асинхронно)
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class HabitCeleryTest(TestCase):
    """Тест проверка отложенных задач Celery"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            telegram_chat_id="123456789",
        )
        self.habit = Habit.objects.create(
            owner=self.user,
            place="Парк",
            time=time(12, 0),
            action="Прогулка",
            reward="Шоколадка",
            periodicity=1,
            duration=60,
        )

    @patch("htracker.tasks.send_telegram_message")
    def test_send_reminder_task(self, mock_send_telegram):
        """Проверка работы напоминающей задачи"""
        result = send_reminder(self.habit.id)
        self.assertIsNone(result)
        mock_send_telegram.assert_called()

    @patch("htracker.tasks.send_telegram_message")
    def test_send_failure_task(self, mock_send_telegram):
        """Проверка работы проваленной задачи"""
        result = send_failure(self.habit.id)
        self.assertIsNone(result)
        mock_send_telegram.assert_called()
        self.habit.refresh_from_db()
        self.assertEqual(self.habit.status, "failed")

    @patch("htracker.tasks.send_telegram_message")
    def test_send_telegram_message_task_failure_retries(self, mock_send_telegram):
        """Тест падения задачи в ошибку"""
        mock_send_telegram.side_effect = Exception("Telegram API error")
        with self.assertRaises(Exception):
            send_telegram_message_task("123456789", "test message")
        self.assertEqual(mock_send_telegram.call_count, 1)

    @patch("htracker.tasks.send_telegram_message_task.delay")
    def test_reminder_and_failure_habit_not_exists(self, mock_send_telegram):
        """Тест: задачи не падают, если привычка не существует"""
        # Проверяем send_reminder
        result1 = send_reminder(999999)
        self.assertIsNone(result1)

        # Проверяем send_failure
        result2 = send_failure(999999)
        self.assertIsNone(result2)
        mock_send_telegram.assert_not_called()

    @patch("htracker.tasks.send_reminder.delay")
    @patch("htracker.tasks.send_failure.delay")
    def test_check_all_habits_no_reminder_no_failure(
        self, mock_send_failure, mock_send_reminder
    ):
        """Тест: привычка не требует напоминания и не проваливается"""

        habit = Habit.objects.create(
            owner=self.user,
            place="Дом",
            time=time(10, 0),
            action="Медитация",
            reward="Шоколадка",
            periodicity=3,  # Периодичность = 3 дня - напоминание не нужно
            duration=60,
            status="started",
            # Прошло 1 день < 7 - провала не будет
            last_completed_at=timezone.now() - timedelta(days=1),
            # Привычка создана 1 день назад, последнее выполнение 1 день назад
            created_at=timezone.now() - timedelta(days=1),
        )
        check_all_habits()

        # Задачи должны ни разу не вызаваться
        mock_send_reminder.assert_not_called(habit.id)
        mock_send_failure.assert_not_called(habit.id)
