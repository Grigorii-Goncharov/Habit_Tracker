from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import time
from htracker.models import Habit
from users.models import User


class HabitPermissionsTest(TestCase):
    """Тест проверка прав доступа"""
    def setUp(self):
        self.client = APIClient()
        self.admin1 = User.objects.create_user(
            email='admin1@example.com',
            password='pass123',
            is_superuser=True,
            is_staff=True,
        )
        self.admin = User.objects.create_superuser(
            email='admin@example.com',
            password='pass123'
        )
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123'
        )
        self.habit = Habit.objects.create(
            owner=self.user1,
            place='Дом',
            time=time(10, 0),
            action='Медитация',
            reward='Шоколадка',
            periodicity=1,
            duration=60
        )

    def test_user_view_habit(self):
        """Проверка просмотра своей привычки"""
        self.client.force_authenticate(user=self.user1)
        data = {'action': 'Новое действие'}
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_all_view_habit(self):
        """Проверка просмотра админом всех привычек(разное создание)"""
    #Админ
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    #Пользователь с правами
        self.client.force_authenticate(user=self.admin1)
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_update_habit(self):
        """Проверка обновления не своей привычки(запрет)"""
        self.client.force_authenticate(user=self.user2)
        data = {'action': 'Новое действие'}
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id}),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete_habit(self):
        """Проверка удаления не своей привычки(запрет)"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_public_habit_readable_by_others(self):
        """Просмотр не владельцем публичных привычек"""
        self.habit.is_public = True
        self.habit.save()
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notauthenticate_nothing(self):
        """Проверка на запрет всего неавторизованным"""
        # Просмотр публичных привычек
        response = self.client.get(
            reverse('htracker:htracker-list')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Просмотр детально
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Обновление
        data = {'action': 'Новое действие'}
        response = self.client.patch(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id}), data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Удаление
        response = self.client.delete(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Создание
        data = {
            'place': "Дом",
            'time': "10:10:00",
            'action': 'Медитация',
            'reward': 'Шоколадка',
            'periodicity': 1,
            'duration': 60
        }
        response = self.client.post(
            reverse('htracker:htracker-list'), data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simpleuser_lock_privatehabit(self):
        """Тест запрета обычным пользователем(не админ и не владелец) доступ к приватной привычке"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(
            reverse('htracker:htracker-detail', kwargs={'pk': self.habit.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

