from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import HtrackerConfig
from .views import HabitViewSet


app_name = HtrackerConfig.name

router = DefaultRouter()
router.register(r'htracker', HabitViewSet, basename='htracker')

urlpatterns = [
    path('', include(router.urls)),
]
