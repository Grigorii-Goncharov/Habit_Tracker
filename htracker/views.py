from django.utils import timezone

from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnlyForPublic
from .tasks import send_telegram_message_task

class HabitPagination(PageNumberPagination):
    """Пагинация для вывода списка привычек на странице"""
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class HabitViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели привычки с разделением прав и сереализатором"""
    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    # Замена IsAuthenticated - неавторизованный может посмотреть публичное
    permission_classes = [IsOwnerOrReadOnlyForPublic, IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_public']
    ordering_fields = ['time', 'periodicity']
    ordering = ['time']

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            # Анонимный пользователь видит только публичные привычки
            if self.action == 'list':
                return Habit.objects.filter(is_public=True)
            else:
                # Для деталей тоже только публичные
                return Habit.objects.filter(is_public=True)

        if user.is_staff:
            return Habit.objects.all()

        # Для списка: свои + публичные
        if self.action == 'list':
            return Habit.objects.filter(
                owner=user
            ) | Habit.objects.filter(is_public=True)

        # Для retrieve/update/delete: только свои или публичные (но редактировать нельзя)
        return Habit.objects.filter(owner=user) | Habit.objects.filter(is_public=True)

    def perform_create(self, serializer):
        habit = serializer.save(owner=self.request.user)
        tg_id = habit.owner.telegram_chat_id

        if not tg_id:
            return

        try:
            if habit.pleasant_habit:
                message = f"Создана новая приятная привычка: {habit.action} в {habit.place}"
            else:
                if habit.reward:
                    message = f"Создана новая привычка: {habit.action} в {habit.place}. Награда: {habit.reward}"
                elif habit.related_habit:
                    related_action = habit.related_habit.action
                    message = f"Создана новая привычка: {habit.action} в {habit.place}. Награда: {related_action}."
                else:
                    message = f"Создана новая привычка: {habit.action} в {habit.place}"

            send_telegram_message_task.delay(chat_id=tg_id, message=message)

        except Exception as e:
            print(f"Ошибка отправки Telegram: {e}")

    def update(self, request, *args, **kwargs):
        """Обработка завершения привычки"""
        response = super().update(request, *args, **kwargs)
        habit = self.get_object()

        if habit.status == 'completed':
            # Обновляем время последнего выполнения
            habit.last_completed_at = timezone.now()
            habit.status = 'started'  # сброс для нового цикла
            habit.save(update_fields=['last_completed_at', 'status'])

            # Отправка награды
            tg_id = habit.owner.telegram_chat_id
            if tg_id:
                try:
                    reward = habit.related_habit.action if habit.related_habit else habit.reward
                    message = f"Привычка '{habit.action}' выполнена! Награда: {reward or 'Отличная работа!'}"
                    send_telegram_message_task.delay(tg_id, message)
                except Exception as e:
                    print(f"Ошибка Telegram при завершении: {e}")

        return response
