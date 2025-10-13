from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from users.models import User
from users.serializers import UserRegisterSerializer, UserProfileSerializer
from users.permissions import IsOwnerOrAdminForProfile


class UserCreateAPIView(CreateAPIView):
    """Регистрация пользователя"""
    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()


class UserListAPIView(ListAPIView):
    """Список всех пользователей — только для админов"""
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]


class UserProfileAPIView(RetrieveUpdateDestroyAPIView):
    """Просмотр, редактирование и удаление профиля"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminForProfile]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        if user_id:
            return User.objects.get(pk=user_id)
        return self.request.user
