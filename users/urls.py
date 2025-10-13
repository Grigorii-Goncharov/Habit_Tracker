from .apps import UsersConfig
from .views import (
    UserCreateAPIview,
    UserListAPIView,
    UserProfileAPIView,
    UserDeleteAPIView,
)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserCreateAPIview.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("list/", UserListAPIView.as_view(), name="user-list"),
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("profile/delete/", UserDeleteAPIView.as_view(), name="user-delete"),
]
