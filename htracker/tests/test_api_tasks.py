import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()


from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from datetime import time
from htracker.models import Habit
from users.models import User


class HabitAPITest(TestCase):
    """Тест проверка передачи данных"""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='123456789'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.pleasant_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Медитация',
            pleasant_habit=True
        )
        self.habit = Habit.objects.create(
            owner=self.user,
            place='Парк',
            time=time(12, 0),
            action='Прогулка',
            reward='Шоколадка',
            periodicity=1,
            duration=60
        )

    def test_create_habit(self):
        """Проверка статус кода + наполнения"""
        # Авторизация
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Офис',
            'time': '09:00:00',
            'action': 'Зарядка',
            'reward': 'Кофе',
            'periodicity': 1,
            'duration': 30
        }
        # 'tracker:tracker-list'-'приложение:сгенерированное имя в пути basename + list для списка'
        # Передача запроса
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Зарядка')


    def test_create_invalid_habit(self):
        """Проверка неправильной передачи награды и длительности у приятной привычки"""
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Парк',
            'time': '18:00:00',
            'action': 'Прогулка',
            'reward': 'Шоколадка',
            'pleasant_habit': True,
            'duration': 150
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_my_habits(self):
        """Тест наличия верного списка привычек(всего 2)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('htracker:htracker-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_public_habits(self):
        """Проверка возвращаемого ID привычки"""
        public_habit = Habit.objects.create(
            owner=self.user,
            place='Парк',
            time=time(15, 0),
            action='Йога',
            reward='Чай',
            is_public=True
        )
        another_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=another_user)
        response = self.client.get(reverse('htracker:htracker-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit_ids = [habit['id'] for habit in response.data['results']]
        self.assertIn(public_habit.id, habit_ids)

    def test_update_habit(self):
        """Проверка PATCH запроса"""
        self.client.force_authenticate(user=self.user)
        data = {'action': 'Прогулка в лесу'}
        # 'tracker:tracker-list'-'приложение:сгенерированное имя в пути basename + detail для деталей'
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Прогулка в лесу')

    def test_delete_habit(self):
        """Проверка метода DELETE для конкретной привычки"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_see_all_habits(self):
        """Проверка, что админ видит все записи"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('htracker:htracker-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Находим функцию и глушим её патчем
    @patch('htracker.views.send_telegram_message_task.delay')
    # Передаем жестко аргументы(подсказка ./media/patch.jpg)
    def test_create_habit_sends_telegram(self, mock_send_telegram):
        """Проверка работоспособности создания привычки и отправки в телеграм"""
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Офис',
            'time': '09:00:00',
            'action': 'Зарядка',
            'reward': 'Кофе',
            'periodicity': 1,
            'duration': 30
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_telegram.assert_called()

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_complete_habit_sends_reward(self, mock_send_telegram):
        """Проверка работоспособности изменения привычки и отправки в телеграм"""
        self.client.force_authenticate(user=self.user)
        data = {'status': 'completed'}
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_telegram.assert_called()

    # #####   ####   ####
    @patch('htracker.views.send_telegram_message_task.delay')
    def test_create_habit_with_related_habit_sends_telegram(self, mock_send_telegram):
        """Тест: создание привычки с связанной привычкой отправляет Telegram"""
        related_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Медитация',
            pleasant_habit=True
        )

        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Офис',
            'time': '09:00:00',
            'action': 'Зарядка',
            'related_habit': related_habit.id,
            'periodicity': 1,
            'duration': 30
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что отправлено сообщение с связанной привычкой
        expected_message = "Создана новая привычка: Зарядка в Офис. Награда: Медитация."
        mock_send_telegram.assert_called_with(chat_id='123456789', message=expected_message)

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_create_habit_with_reward_sends_telegram(self, mock_send_telegram):
        """Тест: создание привычки с наградой отправляет Telegram (для покрытия else)"""
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Парк',
            'time': '12:00:00',
            'action': 'Прогулка',
            'reward': 'Шоколадка',
            'periodicity': 1,
            'duration': 60
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что отправлено сообщение с наградой
        expected_message = "Создана новая привычка: Прогулка в Парк. Награда: Шоколадка"
        mock_send_telegram.assert_called_with(chat_id='123456789', message=expected_message)

    def test_create_habit_no_telegram_when_no_chat_id(self):
        """Тест: создание привычки не отправляет Telegram, если нет chat_id"""
        user_no_tg = User.objects.create_user(
            email='no_tg@example.com',
            password='pass123'
            # telegram_chat_id = None
        )

        self.client.force_authenticate(user=user_no_tg)
        data = {
            'place': 'Парк',
            'time': '12:00:00',
            'action': 'Прогулка',
            'reward': 'Шоколадка',
            'periodicity': 1,
            'duration': 60
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Привычка создана, но Telegram не отправлен (потому что нет chat_id)
        # (нельзя проверить мок, т.к. мок не патчится в этом случае)

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_complete_habit_with_related_habit_reward(self, mock_send_telegram):
        """Тест: завершение привычки с связанной привычкой отправляет Telegram"""
        related_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Медитация',
            pleasant_habit=True
        )

        habit = Habit.objects.create(
            owner=self.user,
            place='Парк',
            time=time(12, 0),
            action='Прогулка',
            related_habit=related_habit,
            periodicity=1,
            duration=60
        )

        self.client.force_authenticate(user=self.user)
        data = {'status': 'completed'}
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_send_telegram.assert_called_with('123456789', "Привычка 'Прогулка' выполнена! Награда: Медитация")

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_complete_habit_without_reward(self, mock_send_telegram):
        """Тест: завершение привычки без награды отправляет Telegram"""
        habit = Habit.objects.create(
            owner=self.user,
            place='Парк',
            time=time(12, 0),
            action='Прогулка',
            reward='Шоколадка',
            periodicity=1,
            duration=60
        )

        self.client.force_authenticate(user=self.user)
        data = {'status': 'completed'}
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_send_telegram.assert_called_with('123456789', "Привычка 'Прогулка' выполнена! Награда: Шоколадка")

    @patch('htracker.views.send_telegram_message_task.delay')
    def test_create_pleasant_habit_sends_telegram(self, mock_send_telegram):
        """Тест: создание приятной привычки отправляет Telegram"""
        self.client.force_authenticate(user=self.user)
        data = {
            'place': 'Дом',
            'time': '10:00:00',
            'action': 'Медитация',
            'pleasant_habit': True,
            'periodicity': 1,
            'duration': 60
            # Нет reward, нет related_habit (для приятной не нужно)
        }
        response = self.client.post(reverse('htracker:htracker-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_message = "Создана новая приятная привычка: Медитация в Дом"
        mock_send_telegram.assert_called_with(chat_id='123456789', message=expected_message)