"""Конфигурация приложения catalog."""
from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Конфиг приложения электронного каталога научных мероприятий."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'
    verbose_name = 'Электронный каталог научных мероприятий'
