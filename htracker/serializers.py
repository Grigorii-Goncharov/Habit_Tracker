from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('owner',)

    def validate(self, data):
        # Повторная валидация на уровне сериализатора (на всякий случай)
        habit = Habit(**data)
        habit.clean()
        return data

