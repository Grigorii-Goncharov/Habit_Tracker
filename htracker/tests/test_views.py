import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.urls import reverse
from rest_framework.test import APITestCase
from unittest.mock import patch
from datetime import time
from htracker.models import Habit
from users.models import User


class HabitViewSetTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='pass123',
            telegram_chat_id='123456789'
        )
        self.client.force_authenticate(user=self.user)

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_perform_create_sends_telegram_pleasant_habit(self, mock_send_telegram):
        data = {
            'place': 'Дом',
            'time': '10:00',  # DRF ожидает строку для time в JSON
            'action': 'Медитация',
            'pleasant_habit': True,
            'periodicity': 1,
            'duration': 60
        }
        url = reverse('htracker:htracker-list')
        response = self.client.post('/htracker/', data, format='json')

        self.assertEqual(response.status_code, 201)
        expected_message = "Создана новая приятная привычка: Медитация в Дом"
        mock_send_telegram.assert_called_once_with(
            chat_id='123456789',
            message=expected_message
        )

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_perform_create_no_telegram_when_no_chat_id(self, mock_send_telegram):
        user_no_tg = User.objects.create_user(
            email='no_tg@example.com',
            password='pass123'
        )
        self.client.force_authenticate(user=user_no_tg)

        data = {
            'place': 'Парк',
            'time': '12:00',
            'action': 'Прогулка',
            'reward': 'Шоколадка',
            'periodicity': 1,
            'duration': 60
        }

        response = self.client.post('/habits/', data, format='json')

        self.assertEqual(response.status_code, 404)
        mock_send_telegram.assert_not_called()

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_perform_create_handles_telegram_error(self, mock_send_telegram):
        mock_send_telegram.side_effect = Exception("Telegram error")

        data = {
            'place': 'Парк',
            'time': '12:00',
            'action': 'Прогулка',
            'reward': 'Шоколадка',
            'periodicity': 1,
            'duration': 60
        }

        url = reverse('htracker:htracker-list')
        response = self.client.post('/htracker/', data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Habit.objects.filter(action='Прогулка').exists())

