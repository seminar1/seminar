"""Модели приложения users.

Определяют кастомную модель пользователя с системой ролей:

- ``ADMIN`` — администратор сервиса (создаётся через ``createsuperuser``
  или назначается вручную).
- ``CURATOR`` — куратор, назначается администратором; в дальнейшем
  получит собственную панель для управления мероприятиями.
- ``USER`` — обычный пользователь, роль по умолчанию для всех,
  кто регистрируется на сайте.
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    """Менеджер пользователей с автоматической ролью администратора."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Создаёт суперпользователя и назначает ему роль администратора."""
        extra_fields.setdefault('role', User.Role.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class User(AbstractUser):
    """Пользователь электронного каталога научных мероприятий."""

    class Role(models.TextChoices):
        """Возможные роли пользователей сервиса."""

        ADMIN = 'admin', 'Администратор'
        CURATOR = 'curator', 'Куратор'
        USER = 'user', 'Пользователь'

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text=(
            'Администратор назначается автоматически для суперпользователя. '
            'Кураторы назначаются администратором из обычных пользователей.'
        ),
    )

    patronymic = models.CharField(
        'Отчество',
        max_length=150,
        blank=True,
    )
    phone = models.CharField(
        'Телефон',
        max_length=32,
        blank=True,
    )
    organization = models.CharField(
        'Организация / подразделение',
        max_length=255,
        blank=True,
        help_text='Например, факультет, кафедра или внешняя организация.',
    )
    position = models.CharField(
        'Должность / статус',
        max_length=255,
        blank=True,
        help_text='Например, студент, преподаватель, научный сотрудник.',
    )

    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        """Возвращает полное имя пользователя или username."""
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        """Поддерживает согласованность роли с флагом ``is_superuser``."""
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Возвращает ФИО с учётом отчества, если оно заполнено."""
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(part for part in parts if part).strip()

    @property
    def is_administrator(self):
        """Является ли пользователь администратором сервиса."""
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_curator(self):
        """Является ли пользователь куратором."""
        return self.role == self.Role.CURATOR

    @property
    def is_regular_user(self):
        """Обычный пользователь без расширенных прав."""
        return self.role == self.Role.USER and not self.is_administrator

    @property
    def role_label(self):
        """Человекочитаемое название роли для отображения в интерфейсе."""
        return self.get_role_display()
