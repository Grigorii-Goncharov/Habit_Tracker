from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели привычки"""
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('owner',)

    def validate(self, data):
        # Валидация модели только при создании
        if not self.instance:
            temp = Habit(**data)
            temp.clean()
        return data

