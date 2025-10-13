from rest_framework import serializers
from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "city", "phone", "telegram_chat_id"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля (чтение и обновление)"""
    class Meta:
        model = User
        fields = ["username", "email", "city", "phone", "telegram_chat_id", "date_joined"]
        read_only_fields = ["email", "date_joined"]  # email и дата — только чтение
