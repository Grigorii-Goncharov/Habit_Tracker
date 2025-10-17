import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.test import TestCase
from datetime import time
from htracker.models import Habit
from users.models import User
from django.core.exceptions import ValidationError


class HabitModelTest(TestCase):
    """Тест создания данных из моделей"""
    def setUp(self):
        """Предустановка модели привычки"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.pleasant_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            pleasant_habit=True
        )

    def test_create_habit(self):
        """Тест создания полезной привычки(по умолчанию False)"""
        habit = Habit.objects.create(
            owner=self.user,
            place='Парк',
            time=time(12, 0),
            action='Прогулка',
            reward='Шоколадка',
            periodicity=1,
            duration=60
        )
        self.assertEqual(str(habit), 'Прогулка в Парк в 12:00:00')
        self.assertEqual(habit.owner, self.user)

    def test_duration_validation(self):
        """Тест нарушения длительности(более 2-ух минут)"""
        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            duration=150
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_periodicity_validation(self):
        """Тест нарушения переодичности(более 7 дней)"""
        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            periodicity=10
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_pleasant_habit_validation(self):
        """Тест на награду у приятной привычки(запрет)"""
        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            pleasant_habit=True,
            reward='Шоколадка'
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_habit_none_reward_and_pleasant_habit(self):
        """Тест на отсутствие любой награды у полезной привычки"""
        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Убрать комнату',
            pleasant_habit=False,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_habit_all_reward(self):
        """Тест на применение награды и приятной привычки(запрет)"""
        test_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Шоколадка',
            pleasant_habit=True,
        )

        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Убрать комнату',
            pleasant_habit=False,
            related_habit=test_habit,
            reward='Шоколадка',
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_related_habit_validation(self):
        """Проверка связи приятной привычки у полезной"""
        not_pleasant_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Бег',
            reward='Шоколадка',
            pleasant_habit=False
        )

        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            related_habit=not_pleasant_habit,
            pleasant_habit=True,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_habit_validation(self):
        """Тест запрет связки двух приятных привычек"""
        not_pleasant_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Бег',
            reward='Шоколадка',
            pleasant_habit=True
        )

        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            related_habit=not_pleasant_habit,
            pleasant_habit=True,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_not_habit_validation(self):
        """Тест запрет связки двух полезных привычек"""
        not_pleasant_habit = Habit.objects.create(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Бег',
            reward='Шоколадка',
        )

        habit = Habit(
            owner=self.user,
            place='Дом',
            time=time(10, 0),
            action='Пить воду',
            related_habit=not_pleasant_habit,
        )
        with self.assertRaises(ValidationError):
            habit.full_clean()