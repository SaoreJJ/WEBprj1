from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager  # Импортируйте созданный менеджер


class User(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=35, verbose_name='Телефон', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Город', blank=True, null=True)
    avatar = models.ImageField(upload_to='users/avatars/', verbose_name='Аватар', blank=True, null=True)

    objects = UserManager()  # Используем кастомный менеджер

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email и пароль требуются по умолчанию

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email