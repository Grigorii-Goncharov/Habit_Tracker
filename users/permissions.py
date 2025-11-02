from rest_framework import permissions


class IsOwnerOrAdminForProfile(permissions.BasePermission):
    """
    Разрешает:
    - Владельцу: полный доступ (GET, PUT, PATCH, DELETE)
    - Админу: только просмотр (GET)
    - Остальным: запрет
    """

    def has_object_permission(self, request, view, obj):
        # Владелец — всё может
        if obj == request.user:
            return True

        # Админ — только чтение
        if request.method == "GET" and request.user.is_staff:
            return True

        return False
