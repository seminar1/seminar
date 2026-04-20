"""Конфигурация приложения users."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Настройки приложения для пользователей электронного каталога."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'
