from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from users.models import User
from users.permissions import IsOwnerOrAdminForProfile
from users.serializers import UserProfileSerializer, UserRegisterSerializer
from users.services import send_telegram_message


class UserCreateAPIView(CreateAPIView):
    """Регистрация пользователя"""

    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        if user.telegram_chat_id:
            try:
                send_telegram_message(
                    chat_id=user.telegram_chat_id,
                    message=" Добро пожаловать! Вы успешно зарегистрировались в трекере привычек.",
                )
            except Exception as e:
                print(f"Ошибка отправки Telegram: {e}")


class UserListAPIView(ListAPIView):
    """Список всех пользователей — только для админов"""

    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]


class UserProfileAPIView(RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление своего профиля"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminForProfile]

    def get_object(self):
        # Работаем только со своим профилем
        return self.request.user
