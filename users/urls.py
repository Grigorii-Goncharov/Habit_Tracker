from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UsersConfig
from .views import UserCreateAPIView, UserListAPIView, UserProfileAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("list/", UserListAPIView.as_view(), name="user-list"),
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
