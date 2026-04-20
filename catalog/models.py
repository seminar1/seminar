"""Модели приложения catalog.

Определяют структуру данных для электронного каталога научных
мероприятий: справочники (научные направления, типы событий)
и основную сущность `Event` с регистрациями участников.
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Direction(models.Model):
    """Научное направление мероприятия (справочник)."""

    title = models.CharField('Название', max_length=120, unique=True)
    slug = models.SlugField('Слаг', max_length=120, unique=True, allow_unicode=True)
    icon = models.CharField(
        'Иконка',
        max_length=60,
        default='bi-bookmark',
        help_text='CSS-класс иконки Bootstrap Icons, например «bi-cpu».',
    )
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активное', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Научное направление'
        verbose_name_plural = 'Научные направления'
        ordering = ['title']

    def __str__(self):
        """Возвращает название направления."""
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически формирует slug, если он не задан."""
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class EventType(models.Model):
    """Тип научного мероприятия (конференция, семинар, лекция и т.д.)."""

    title = models.CharField('Название', max_length=80, unique=True)
    slug = models.SlugField('Слаг', max_length=80, unique=True, allow_unicode=True)
    icon = models.CharField(
        'Иконка',
        max_length=60,
        default='bi-calendar2-event',
        help_text='CSS-класс иконки Bootstrap Icons.',
    )
    is_active = models.BooleanField('Активное', default=True)

    class Meta:
        verbose_name = 'Тип мероприятия'
        verbose_name_plural = 'Типы мероприятий'
        ordering = ['title']

    def __str__(self):
        """Возвращает название типа мероприятия."""
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически формирует slug, если он не задан."""
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class Event(models.Model):
    """Научное мероприятие электронного каталога."""

    class Format(models.TextChoices):
        """Форматы проведения мероприятия."""

        OFFLINE = 'offline', 'Очно'
        ONLINE = 'online', 'Дистанционно'
        HYBRID = 'hybrid', 'Гибридный'

    class Status(models.TextChoices):
        """Статус жизненного цикла мероприятия."""

        DRAFT = 'draft', 'Черновик'
        PUBLISHED = 'published', 'Опубликовано'
        CANCELLED = 'cancelled', 'Отменено'
        COMPLETED = 'completed', 'Завершено'

    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('Слаг', max_length=255, unique=True, allow_unicode=True)
    short_description = models.CharField(
        'Краткое описание',
        max_length=500,
        blank=True,
        help_text='Показывается в карточке в каталоге (до 500 символов).',
    )
    description = models.TextField('Полное описание', blank=True)

    direction = models.ForeignKey(
        Direction,
        verbose_name='Научное направление',
        on_delete=models.PROTECT,
        related_name='events',
    )
    event_type = models.ForeignKey(
        EventType,
        verbose_name='Тип мероприятия',
        on_delete=models.PROTECT,
        related_name='events',
    )
    event_format = models.CharField(
        'Формат',
        max_length=20,
        choices=Format.choices,
        default=Format.OFFLINE,
    )

    starts_at = models.DateTimeField('Начало')
    ends_at = models.DateTimeField('Окончание', blank=True, null=True)

    location = models.CharField(
        'Место проведения',
        max_length=255,
        blank=True,
        help_text='Адрес или название аудитории для очных форматов.',
    )
    online_url = models.URLField(
        'Ссылка на трансляцию',
        blank=True,
        help_text='Используется для дистанционного и гибридного формата.',
    )

    seats_total = models.PositiveIntegerField(
        'Всего мест',
        default=0,
        help_text='0 — без ограничения по количеству участников.',
    )

    cover = models.ImageField(
        'Обложка',
        upload_to='events/covers/%Y/%m/',
        blank=True,
        null=True,
    )

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Организатор',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    is_featured = models.BooleanField(
        'Рекомендуемое',
        default=False,
        help_text='Показывается на главной странице.',
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['-starts_at']
        indexes = [
            models.Index(fields=['-starts_at']),
            models.Index(fields=['status', '-starts_at']),
            models.Index(fields=['event_format']),
        ]

    def __str__(self):
        """Возвращает название мероприятия."""
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически формирует slug, если он не задан."""
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)[:255]
        super().save(*args, **kwargs)

    @property
    def seats_taken(self):
        """Количество подтверждённых регистраций участников."""
        return self.registrations.filter(
            status=EventRegistration.Status.CONFIRMED
        ).count()

    @property
    def seats_available(self):
        """Количество свободных мест, либо None, если лимита нет."""
        if self.seats_total == 0:
            return None
        return max(self.seats_total - self.seats_taken, 0)

    @property
    def is_full(self):
        """Все места заняты."""
        return self.seats_total > 0 and self.seats_available == 0

    @property
    def is_registration_open(self):
        """Доступна ли регистрация на мероприятие."""
        return self.status == self.Status.PUBLISHED and not self.is_full


class EventRegistration(models.Model):
    """Заявка пользователя на участие в мероприятии."""

    class Status(models.TextChoices):
        """Статус заявки участника."""

        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        CANCELLED = 'cancelled', 'Отменена'
        WAITLIST = 'waitlist', 'Лист ожидания'
        ATTENDED = 'attended', 'Посетил(а)'

    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Участник',
        on_delete=models.CASCADE,
        related_name='event_registrations',
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    note = models.TextField(
        'Комментарий участника',
        blank=True,
        help_text='Дополнительная информация от участника (опционально).',
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Регистрация на мероприятие'
        verbose_name_plural = 'Регистрации на мероприятия'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'user'],
                name='unique_event_user_registration',
            ),
        ]
        indexes = [
            models.Index(fields=['event', 'status']),
        ]

    def __str__(self):
        """Возвращает строку вида «Участник → Мероприятие»."""
        return f'{self.user} → {self.event}'
