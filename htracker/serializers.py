from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для модели привычки"""

    class Meta:
        model = Habit
        fields = (
            "owner",
            "id",
            "place",
            "time",
            "action",
            "pleasant_habit",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "status",
            "created_at",
            "last_completed_at",
        )
        read_only_fields = ("owner", "last_completed_at", "created_at")

    def validate(self, data):
        if not self.instance:
            owner = self.context["request"].user
            temp = Habit(owner=owner, **data)
            temp.clean()
        return data
