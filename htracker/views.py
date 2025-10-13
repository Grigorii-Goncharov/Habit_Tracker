from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnlyForPublic


class HabitPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class HabitViewSet(viewsets.ModelViewSet):
    """ Вьюсет для модели "Habit"  """

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [IsOwnerOrReadOnlyForPublic]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_public']
    ordering_fields = ['time', 'periodicity']
    ordering = ['time']

    def get_queryset(self):
        """
        - Админ видит всё.
        - Обычный пользователь:
            * В списке — только свои привычки + публичные других.
            * При детальном просмотре — свои или публичные.
        """
        user = self.request.user
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
        serializer.save(owner=self.request.user)
