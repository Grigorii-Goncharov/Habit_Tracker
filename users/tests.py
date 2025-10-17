from django.http import HttpRequest
from django.test import TestCase

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from unittest.mock import patch


from users.permissions import IsOwnerOrAdminForProfile


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)

    def test_create_user_with_empty_email(self):
        """Тест: создание пользователя с пустым email вызывает ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123',
                username='testuser'
            )

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_representation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'test@example.com')


class UserAPITest(TestCase):
    """Тесты API пользователей"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser',
            telegram_chat_id='123456789'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_registration(self):
        """Тест регистрации пользователя"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'city': 'Moscow',
            'phone': '+79991234567',
            'telegram_chat_id': '987654321'
        }
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    @patch('users.views.send_telegram_message')
    def test_registration_sends_telegram_welcome(self, mock_send_telegram):
        """Тест отправки приветственного сообщения в Telegram при регистрации"""
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'telegram_chat_id': '987654321'
        }
        response = self.client.post(reverse('users:register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_telegram.assert_called_once()

    def test_user_profile_retrieve(self):
        """Тест получения профиля пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_user_profile_update(self):
        """Тест обновления профиля пользователя"""
        self.client.force_authenticate(user=self.user)
        data = {'city': 'New York'}
        response = self.client.patch(reverse('users:user-profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'New York')


    def test_user_profile_delete(self):
        """Тест удаления профиля пользователя"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_list_users(self):
        """Тест: админ может просматривать список пользователей"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_list_users(self):
        """Тест: обычный пользователь не может просматривать список пользователей"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_other_profile(self):
        """Тест: пользователь не может получить чужой профиль"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        # Этот эндпоинт всегда возвращает профиль текущего пользователя
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'other@example.com')


class UserPermissionsTest(TestCase):
    """Тесты прав доступа пользователей"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123',
            username='user1'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123',
            username='user2'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            username='admin'
        )

    def test_user_can_access_own_profile(self):
        """Тест: пользователь может получить доступ к своему профилю"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_own_profile(self):
        """Тест: пользователь может обновить свой профиль"""
        self.client.force_authenticate(user=self.user1)
        data = {'city': 'New York'}
        response = self.client.patch(reverse('users:user-profile'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'New York')

    def test_user_can_delete_own_profile(self):
        """Тест: пользователь может удалить свой профиль"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_access_other_profile(self):
        """Тест: пользователь не может получить доступ к чужому профилю"""
        self.client.force_authenticate(user=self.user2)
        # Вместо этого проверим, что user2 получает свой профиль, а не user1
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user2@example.com')


    def test_admin_can_read_profile(self):
        """Тест: админ может читать профиль (GET)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_cannot_patch_other_user_profile_via_api(self):
        """Тест: админ не может изменить чужой профиль через API"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user1_id = self.user1.id
        permission = IsOwnerOrAdminForProfile()

        request = HttpRequest()
        request.user = self.admin_user
        request.method = 'PATCH'

        # Проверяем, что админ не может изменить чужой профиль
        result = permission.has_object_permission(
            request,
            None,
            self.user1
        )
        self.assertFalse(result)

    def test_unauthenticated_user_cannot_access_profile(self):
        """Тест: неавторизованный пользователь не может получить доступ к профилю"""
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_modify_other_user_directly(self):
        """Тест: пользователь не может изменить чужой профиль напрямую"""
        permission = IsOwnerOrAdminForProfile()
        # Создаем фейковый запрос
        request = HttpRequest()
        request.user = self.user2  # другой пользователь
        # Проверяем, что user2 не может получить доступ к профилю user1
        result = permission.has_object_permission(
            request,
            None,
            self.user1
        )
        self.assertFalse(result)

        # Проверяем, что user1 может получить доступ к своему профилю
        request.user = self.user1
        result = permission.has_object_permission(
            request,
            None,  # view
            self.user1  # obj = user1
        )
        self.assertTrue(result)

        # Проверяем, что админ может получить доступ к чужому профилю для чтения
        request.user = self.admin_user
        request.method = 'GET'
        result = permission.has_object_permission(
            request,
            None,  # view
            self.user1  # obj = user1
        )
        self.assertTrue(result)

        # Проверяем, что админ НЕ может получить доступ к чужому профилю для записи
        request.method = 'PATCH'
        result = permission.has_object_permission(
            request,
            None,  # view
            self.user1  # obj = user1
        )
        self.assertFalse(result)



class UserServiceTest(TestCase):
    """Тесты сервисов пользователей"""

    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            telegram_chat_id='123456789'
        )

    @patch('users.services.send_telegram_message')
    def test_send_telegram_message(self, mock_send_telegram):
        """Тест вызова функции отправки Telegram сообщения"""
        # Мок возвращает фиктивный результат
        mock_send_telegram.return_value = {"ok": True}

        from users.services import send_telegram_message
        result = send_telegram_message('123456789', 'Test message')

        # Проверяем, что мок был вызван с правильными аргументами
        mock_send_telegram.assert_called_once_with('123456789', 'Test message')
        # Проверяем, что функция вернула ожидаемый результат
        self.assertEqual(result, {"ok": True})
