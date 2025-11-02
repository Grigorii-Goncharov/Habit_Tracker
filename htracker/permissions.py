from rest_framework import permissions


class IsOwnerOrReadOnlyForPublic(permissions.BasePermission):
    """Переопределение прав между админом и юзером"""

    # Перредаем ссылку класса, запрос, вьюсет и конкретный объект к которому обращаемся
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS - безопасные методы
        SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

        # 1. Любой может ЧИТАТЬ публичные привычки
        if request.method in SAFE_METHODS and obj.is_public:
            return True

        # 2. Владелец может ЧИТАТЬ свои привычки
        if request.method in SAFE_METHODS and obj.owner == request.user:
            return True

        # 3. Админ может ЧИТАТЬ все привычки
        if request.method in SAFE_METHODS and request.user.is_staff:
            return True

        # 4. Владелец может ИЗМЕНЯТЬ/УДАЛЯТЬ свои привычки
        if request.method not in SAFE_METHODS and obj.owner == request.user:
            return True

        # 5. Никто другой не может ничего
        return False
