from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

urlpatterns = [
    # Основные
    path("admin/", admin.site.urls),
    path("", include("htracker.urls", namespace="htracker")),
    path("users/", include("users.urls", namespace="users")),
    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # UI документации
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Дополнительно: Swagger UI по короткому пути /swagger/
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT or settings.STATICFILES_DIRS[0],
    )
