from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Имя пользователя",
        unique=True,
    )
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Телефон должен быть в формате: '+999999999'. До 15 цифр.",
            )
        ],
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")

    telegram_chat_id = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Telegram Chat ID"
    )

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
