from django.core.exceptions import ValidationError
from django.db import models
from users.models import User


class Habit(models.Model):

    STARTED = 'started'
    COMPLETED = 'completed'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (STARTED, 'запущена'),
        (COMPLETED, 'выполнена'),
        (FAILED, 'провалена'),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name="Владелец"
    )
    place = models.CharField(max_length=100, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=150, verbose_name="Действие")

    pleasant_habit = models.BooleanField(default=False, verbose_name="Приятная привычка")

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'pleasant_habit': True},
        verbose_name="Связанная приятная привычка"
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность (в днях)"
    )

    reward = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Вознаграждение"
    )

    duration = models.PositiveSmallIntegerField(
        default=120,
        verbose_name="Время на выполнение (в секундах)"
    )

    is_public = models.BooleanField(default=False, verbose_name="Публичная")

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STARTED)

    def clean(self):
        if self.duration > 120:
            raise ValidationError("Время на выполнение не должно превышать 120 секунд.")

        if not (1 <= self.periodicity <= 7):
            raise ValidationError("Периодичность должна быть от 1 до 7 дней.")

        if self.pleasant_habit:
            if self.reward or self.related_habit:
                raise ValidationError(
                    "Приятная привычка не может иметь вознаграждение или связанную привычку."
                )
        else:
            if self.reward and self.related_habit:
                raise ValidationError(
                    "Укажите либо вознаграждение, либо связанную приятную привычку."
                )
            if not self.reward and not self.related_habit:
                raise ValidationError(
                    "Полезная привычка должна иметь вознаграждение или связанную приятную привычку."
                )
            if self.related_habit and not self.related_habit.pleasant_habit:
                raise ValidationError(
                    "Связанная привычка должна быть приятной."
                )

    def __str__(self):
        return f"{self.action} в {self.place} в {self.time}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
