"""Модели приложения catalog.

Определяют структуру данных для электронного каталога научных
мероприятий: справочники (научные направления, типы событий),
основную сущность ``Event`` и систему регистраций участников
``EventRegistration`` со снимком контактных данных, управлением
листом ожидания и отслеживанием жизненного цикла заявки.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

RU_MONTHS_SHORT = [
    'янв', 'фев', 'мар', 'апр', 'май', 'июн',
    'июл', 'авг', 'сен', 'окт', 'ноя', 'дек',
]
RU_MONTHS_GENITIVE = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]


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

    registration_opens_at = models.DateTimeField(
        'Старт приёма заявок',
        blank=True,
        null=True,
        help_text=(
            'Если не заполнено, заявки принимаются сразу после '
            'публикации мероприятия.'
        ),
    )
    registration_closes_at = models.DateTimeField(
        'Окончание приёма заявок',
        blank=True,
        null=True,
        help_text=(
            'Если не заполнено, заявки принимаются до момента начала '
            'мероприятия.'
        ),
    )
    requires_approval = models.BooleanField(
        'Требуется подтверждение куратора',
        default=False,
        help_text=(
            'Новые заявки получают статус «Ожидает подтверждения» и '
            'подтверждаются куратором вручную.'
        ),
    )
    allow_waitlist = models.BooleanField(
        'Разрешить лист ожидания',
        default=True,
        help_text='Если мест нет, новые заявки попадают в лист ожидания.',
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
    def pending_count(self):
        """Количество заявок, ожидающих подтверждения куратором."""
        return self.registrations.filter(
            status=EventRegistration.Status.PENDING
        ).count()

    @property
    def waitlist_count(self):
        """Количество заявок в листе ожидания."""
        return self.registrations.filter(
            status=EventRegistration.Status.WAITLIST
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
    def is_registration_time_active(self):
        """Находится ли текущий момент внутри окна приёма заявок.

        Границы окна необязательные: отсутствие ``registration_opens_at``
        означает «принимаем сразу», а отсутствие ``registration_closes_at``
        — «принимаем до начала мероприятия».
        """
        now = timezone.now()
        if self.registration_opens_at and now < self.registration_opens_at:
            return False
        upper_bound = self.registration_closes_at or self.starts_at
        return now < upper_bound

    @property
    def is_registration_open(self):
        """Доступен ли приём заявок на участие в мероприятии.

        Учитывает статус мероприятия, наличие свободных мест
        (либо возможность попасть в лист ожидания) и временное окно
        приёма заявок.
        """
        if self.status != self.Status.PUBLISHED:
            return False
        if not self.is_registration_time_active:
            return False
        if self.is_full and not self.allow_waitlist:
            return False
        return True

    @property
    def date_day(self):
        """День начала мероприятия в формате «24»."""
        return f'{self.starts_at.day:02d}'

    @property
    def date_month_short(self):
        """Сокращённое название месяца начала на русском («апр»)."""
        return RU_MONTHS_SHORT[self.starts_at.month - 1]

    @property
    def date_full(self):
        """Полная дата начала на русском («24 апреля 2026»)."""
        month = RU_MONTHS_GENITIVE[self.starts_at.month - 1]
        return f'{self.starts_at.day} {month} {self.starts_at.year}'

    @property
    def time_range(self):
        """Время проведения: «10:00 — 18:00» или «10:00», если нет окончания."""
        start = self.starts_at.strftime('%H:%M')
        if not self.ends_at:
            return start
        return f'{start} — {self.ends_at.strftime("%H:%M")}'

    @property
    def status_slug(self):
        """Короткий статус для визуального оформления карточки."""
        if self.is_full:
            return 'full'
        if self.is_registration_open:
            return 'open'
        return 'closed'

    @property
    def status_label(self):
        """Текстовый статус карточки для отображения пользователю."""
        if self.is_full:
            return 'Мест нет'
        if self.is_registration_open:
            return 'Регистрация открыта'
        if self.status == self.Status.CANCELLED:
            return 'Отменено'
        if self.status == self.Status.COMPLETED:
            return 'Завершено'
        return 'Скоро'

    @property
    def seats_percent(self):
        """Процент заполненности мест (0–100). 0, если без ограничения."""
        if self.seats_total == 0:
            return 0
        return min(int(round(self.seats_taken * 100 / self.seats_total)), 100)

    def clean(self):
        """Проверяет согласованность полей регистрационного окна."""
        super().clean()
        if (
            self.registration_opens_at
            and self.registration_closes_at
            and self.registration_opens_at >= self.registration_closes_at
        ):
            raise ValidationError({
                'registration_closes_at': (
                    'Окончание приёма заявок должно быть позже их старта.'
                ),
            })
        if self.registration_closes_at and self.registration_closes_at > self.starts_at:
            raise ValidationError({
                'registration_closes_at': (
                    'Приём заявок не может завершаться позже начала '
                    'мероприятия.'
                ),
            })

    def can_user_register(self, user):
        """Может ли указанный пользователь подать заявку на участие.

        Возвращает ``True`` только если регистрация в принципе открыта
        (см. ``is_registration_open``) и у пользователя нет активной
        заявки на это мероприятие.
        """
        if not user or not user.is_authenticated:
            return False
        if not self.is_registration_open:
            return False
        return not self.registrations.filter(
            user=user,
            status__in=EventRegistration.ACTIVE_STATUSES,
        ).exists()

    def get_user_registration(self, user):
        """Возвращает последнюю заявку пользователя на это мероприятие.

        Если заявок нет — ``None``. Используется для отображения текущего
        статуса пользователя в карточке мероприятия.
        """
        if not user or not user.is_authenticated:
            return None
        return (
            self.registrations
            .filter(user=user)
            .order_by('-created_at')
            .first()
        )


class EventRegistration(models.Model):
    """Заявка пользователя на участие в научном мероприятии.

    Помимо связи «мероприятие — участник», хранит снимок контактных
    данных участника на момент подачи заявки (поля профиля могут
    измениться позже), признаки жизненного цикла (подтверждение,
    отмена, причина) и позицию в листе ожидания.
    """

    class Status(models.TextChoices):
        """Статус заявки участника."""

        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждена'
        WAITLIST = 'waitlist', 'Лист ожидания'
        CANCELLED = 'cancelled', 'Отменена'
        ATTENDED = 'attended', 'Посетил(а)'
        NO_SHOW = 'no_show', 'Не явился'

    class Source(models.TextChoices):
        """Способ создания заявки."""

        SELF = 'self', 'Самостоятельно'
        CURATOR = 'curator', 'Добавлен куратором'
        IMPORT = 'import', 'Импорт'

    #: Статусы, при которых заявка считается «живой» (занимает слот
    #: или место в листе ожидания). Используется при проверке повторной
    #: регистрации одного и того же пользователя на одно мероприятие.
    ACTIVE_STATUSES = (
        Status.PENDING,
        Status.CONFIRMED,
        Status.WAITLIST,
    )

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
    source = models.CharField(
        'Источник заявки',
        max_length=20,
        choices=Source.choices,
        default=Source.SELF,
    )

    full_name = models.CharField(
        'ФИО участника',
        max_length=255,
        blank=True,
        help_text='Снимок ФИО на момент подачи заявки.',
    )
    email = models.EmailField(
        'Email для связи',
        blank=True,
        help_text='Контактный email, указанный в заявке.',
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
    )
    position = models.CharField(
        'Должность / статус',
        max_length=255,
        blank=True,
    )

    note = models.TextField(
        'Комментарий участника',
        blank=True,
        help_text='Дополнительная информация от участника (опционально).',
    )

    waitlist_position = models.PositiveIntegerField(
        'Позиция в листе ожидания',
        blank=True,
        null=True,
        help_text=(
            'Заполняется автоматически при постановке заявки в лист '
            'ожидания. Меньшее значение — ближе к подтверждению.'
        ),
    )

    confirmed_at = models.DateTimeField(
        'Подтверждено',
        blank=True,
        null=True,
    )
    cancelled_at = models.DateTimeField(
        'Отменено',
        blank=True,
        null=True,
    )
    cancellation_reason = models.TextField(
        'Причина отмены',
        blank=True,
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Кем отменена',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cancelled_event_registrations',
        help_text='Пользователь, отменивший заявку (участник или куратор).',
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
                condition=models.Q(
                    status__in=['pending', 'confirmed', 'waitlist']
                ),
                name='unique_active_event_user_registration',
            ),
        ]
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'waitlist_position']),
        ]

    def __str__(self):
        """Возвращает строку вида «Участник → Мероприятие»."""
        return f'{self.user} → {self.event}'

    @property
    def is_active(self):
        """Заявка в активном (не отменённом, не исторически-закрытом) статусе."""
        return self.status in self.ACTIVE_STATUSES

    @property
    def is_cancelled(self):
        """Заявка отменена."""
        return self.status == self.Status.CANCELLED

    @property
    def is_waitlisted(self):
        """Заявка в листе ожидания."""
        return self.status == self.Status.WAITLIST

    @property
    def display_full_name(self):
        """ФИО участника с резервным значением из профиля пользователя."""
        if self.full_name:
            return self.full_name
        if self.user_id:
            return self.user.get_full_name() or self.user.username
        return ''

    def populate_snapshot_from_user(self, overwrite=False):
        """Копирует контактные данные из профиля пользователя в заявку.

        Если ``overwrite=False`` (по умолчанию) заполняются только пустые
        поля — так можно безопасно вызывать метод при сохранении формы,
        не теряя уже введённые участником значения.
        """
        if not self.user_id:
            return
        user = self.user
        defaults = {
            'full_name': user.get_full_name() or user.username,
            'email': user.email or '',
            'phone': getattr(user, 'phone', '') or '',
            'organization': getattr(user, 'organization', '') or '',
            'position': getattr(user, 'position', '') or '',
        }
        for field, value in defaults.items():
            if overwrite or not getattr(self, field, ''):
                setattr(self, field, value)

    def mark_confirmed(self, *, save=True):
        """Переводит заявку в подтверждённый статус и фиксирует момент."""
        self.status = self.Status.CONFIRMED
        self.confirmed_at = timezone.now()
        self.waitlist_position = None
        if save:
            self.save(update_fields=[
                'status',
                'confirmed_at',
                'waitlist_position',
                'updated_at',
            ])

    def mark_cancelled(self, *, by=None, reason='', save=True):
        """Отменяет заявку, сохраняя инициатора и причину отмены."""
        self.status = self.Status.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason or ''
        if by is not None and getattr(by, 'is_authenticated', False):
            self.cancelled_by = by
        self.waitlist_position = None
        if save:
            self.save(update_fields=[
                'status',
                'cancelled_at',
                'cancellation_reason',
                'cancelled_by',
                'waitlist_position',
                'updated_at',
            ])

    def place_on_waitlist(self, *, save=True):
        """Ставит заявку в конец листа ожидания мероприятия."""
        last_position = (
            self.event.registrations
            .filter(status=self.Status.WAITLIST)
            .exclude(pk=self.pk)
            .aggregate(models.Max('waitlist_position'))['waitlist_position__max']
        )
        self.status = self.Status.WAITLIST
        self.waitlist_position = (last_position or 0) + 1
        if save:
            self.save(update_fields=[
                'status',
                'waitlist_position',
                'updated_at',
            ])


class EventBookmark(models.Model):
    """Закладка «Избранное»: мероприятие, сохранённое пользователем."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='event_bookmarks',
    )
    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'Закладка (избранное)'
        verbose_name_plural = 'Закладки (избранное)'
        unique_together = ('user', 'event')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """Краткое представление для админки и отладки."""
        return f'{self.user} → {self.event.title}'


class FeedbackTopic(models.Model):
    """Тема (категория) обращения в форме обратной связи.

    Используется как справочник: позволяет администратору управлять
    списком тем сообщений («Вопрос по мероприятию», «Сотрудничество»,
    «Техническая проблема» и т.п.) без изменения кода.
    """

    title = models.CharField('Название', max_length=120, unique=True)
    slug = models.SlugField('Слаг', max_length=120, unique=True, allow_unicode=True)
    description = models.CharField(
        'Краткое описание',
        max_length=255,
        blank=True,
        help_text='Необязательная подсказка для пользователя при выборе темы.',
    )
    icon = models.CharField(
        'Иконка',
        max_length=60,
        default='bi-chat-dots',
        help_text='CSS-класс иконки Bootstrap Icons.',
    )
    order = models.PositiveIntegerField(
        'Порядок',
        default=100,
        help_text='Темы с меньшим значением отображаются выше.',
    )
    is_active = models.BooleanField('Активная', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Тема обращения'
        verbose_name_plural = 'Темы обращений'
        ordering = ['order', 'title']

    def __str__(self):
        """Возвращает название темы."""
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически формирует slug, если он не задан."""
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class FeedbackMessage(models.Model):
    """Сообщение из формы обратной связи.

    Позволяет отправлять обращения как авторизованным, так и анонимным
    пользователям. Для авторизованных пользователей сохраняется ссылка
    на учётную запись (``user``), но контактные данные (ФИО, email,
    телефон) фиксируются «снимком» на момент отправки, чтобы сохранить
    актуальную на тот момент информацию.

    Дополнительно хранятся техническая метаинформация о запросе
    (IP-адрес, User-Agent, реферер), связь с конкретным мероприятием
    (если обращение касается события каталога) и внутренние поля для
    обработки обращений администраторами.
    """

    class Status(models.TextChoices):
        """Статус обработки обращения."""

        NEW = 'new', 'Новое'
        IN_PROGRESS = 'in_progress', 'В работе'
        ANSWERED = 'answered', 'Отвечено'
        CLOSED = 'closed', 'Закрыто'
        SPAM = 'spam', 'Спам'

    class Source(models.TextChoices):
        """Источник, из которого пришло обращение."""

        CONTACT_FORM = 'contact_form', 'Форма обратной связи'
        EVENT_PAGE = 'event_page', 'Страница мероприятия'
        FOOTER = 'footer', 'Подвал сайта'
        OTHER = 'other', 'Другое'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор (если авторизован)',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='feedback_messages',
        help_text=(
            'Ссылка на учётную запись, если сообщение оставил '
            'авторизованный пользователь. Для анонимных обращений — пусто.'
        ),
    )
    topic = models.ForeignKey(
        FeedbackTopic,
        verbose_name='Тема обращения',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='messages',
    )
    related_event = models.ForeignKey(
        Event,
        verbose_name='Связанное мероприятие',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='feedback_messages',
        help_text='Заполняется, если обращение касается конкретного мероприятия.',
    )

    full_name = models.CharField(
        'Имя / ФИО',
        max_length=255,
        help_text='Как к вам обращаться.',
    )
    email = models.EmailField(
        'Email для ответа',
        help_text='Электронная почта, на которую придёт ответ.',
    )
    phone = models.CharField(
        'Телефон',
        max_length=32,
        blank=True,
        help_text='Необязательный контактный телефон.',
    )
    organization = models.CharField(
        'Организация',
        max_length=255,
        blank=True,
        help_text='Необязательно: место работы или учёбы.',
    )

    subject = models.CharField(
        'Тема сообщения',
        max_length=255,
        blank=True,
        help_text='Краткий заголовок обращения.',
    )
    message = models.TextField(
        'Сообщение',
        help_text='Текст обращения.',
    )

    consent_to_processing = models.BooleanField(
        'Согласие на обработку персональных данных',
        default=False,
        help_text='Отмечается пользователем при отправке формы.',
    )
    subscribe_to_news = models.BooleanField(
        'Подписаться на новости',
        default=False,
        help_text='Пользователь согласен получать новостную рассылку.',
    )

    ip_address = models.GenericIPAddressField(
        'IP-адрес',
        blank=True,
        null=True,
        help_text='IP отправителя для анти-спам проверок и аудита.',
    )
    user_agent = models.CharField(
        'User-Agent',
        max_length=500,
        blank=True,
    )
    referer = models.URLField(
        'Реферер',
        max_length=500,
        blank=True,
        help_text='Страница, с которой была отправлена форма.',
    )
    source = models.CharField(
        'Источник',
        max_length=30,
        choices=Source.choices,
        default=Source.CONTACT_FORM,
    )

    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    admin_note = models.TextField(
        'Внутренний комментарий',
        blank=True,
        help_text='Заметки администраторов, не видны пользователю.',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Ответственный',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_feedback_messages',
        help_text='Сотрудник, которому поручено обработать обращение.',
    )

    answered_at = models.DateTimeField(
        'Дата ответа',
        blank=True,
        null=True,
    )
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Кто ответил',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='answered_feedback_messages',
    )
    answer_text = models.TextField(
        'Текст ответа',
        blank=True,
        help_text='Итоговый ответ пользователю (опционально сохраняется для истории).',
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Обращение обратной связи'
        verbose_name_plural = 'Обращения обратной связи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """Возвращает краткое представление обращения для админки."""
        subject = self.subject or (self.topic.title if self.topic_id else 'Без темы')
        return f'{self.full_name} — {subject}'

    @property
    def is_anonymous(self):
        """Оставлено ли обращение анонимным пользователем."""
        return self.user_id is None

    @property
    def is_answered(self):
        """Есть ли ответ на обращение."""
        return self.status == self.Status.ANSWERED and self.answered_at is not None

    @property
    def display_subject(self):
        """Отображаемая тема: явная тема обращения либо название категории."""
        if self.subject:
            return self.subject
        if self.topic_id:
            return self.topic.title
        return 'Без темы'

    def mark_answered(self, *, by=None, answer_text='', save=True):
        """Помечает обращение как отвеченное.

        Сохраняет автора ответа, момент ответа и опционально текст ответа.
        """
        self.status = self.Status.ANSWERED
        self.answered_at = timezone.now()
        if answer_text:
            self.answer_text = answer_text
        if by is not None and getattr(by, 'is_authenticated', False):
            self.answered_by = by
        if save:
            self.save(update_fields=[
                'status',
                'answered_at',
                'answered_by',
                'answer_text',
                'updated_at',
            ])

    def mark_spam(self, *, save=True):
        """Помечает обращение как спам."""
        self.status = self.Status.SPAM
        if save:
            self.save(update_fields=['status', 'updated_at'])


class EventReview(models.Model):
    """Отзыв / оценка мероприятия от участника.

    Отдельная форма обратной связи, привязанная к конкретному
    мероприятию: пользователь (в том числе анонимный) может оставить
    оценку и комментарий. Для авторизованных пользователей сохраняется
    ссылка на учётную запись, для анонимных — только контактный email
    (опционально) и снимок имени.
    """

    class Status(models.TextChoices):
        """Статус модерации отзыва."""

        PENDING = 'pending', 'На модерации'
        PUBLISHED = 'published', 'Опубликован'
        REJECTED = 'rejected', 'Отклонён'
        HIDDEN = 'hidden', 'Скрыт'

    RATING_CHOICES = [
        (1, '1 — очень плохо'),
        (2, '2 — плохо'),
        (3, '3 — нормально'),
        (4, '4 — хорошо'),
        (5, '5 — отлично'),
    ]

    event = models.ForeignKey(
        Event,
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор (если авторизован)',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='event_reviews',
    )

    author_name = models.CharField(
        'Имя автора',
        max_length=255,
        help_text='Как подписать отзыв. Снимок на момент отправки.',
    )
    author_email = models.EmailField(
        'Email автора',
        blank=True,
        help_text='Необязательно для анонимных отзывов.',
    )

    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=RATING_CHOICES,
        help_text='Оценка мероприятия по шкале от 1 до 5.',
    )
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True,
    )
    text = models.TextField(
        'Текст отзыва',
        help_text='Впечатления от мероприятия.',
    )

    pros = models.TextField(
        'Плюсы',
        blank=True,
        help_text='Что особенно понравилось (опционально).',
    )
    cons = models.TextField(
        'Минусы',
        blank=True,
        help_text='Что стоит улучшить (опционально).',
    )

    ip_address = models.GenericIPAddressField(
        'IP-адрес',
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        'User-Agent',
        max_length=500,
        blank=True,
    )

    status = models.CharField(
        'Статус модерации',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    moderation_note = models.TextField(
        'Комментарий модератора',
        blank=True,
        help_text='Причина отклонения или внутренние заметки.',
    )
    moderated_at = models.DateTimeField(
        'Проверено',
        blank=True,
        null=True,
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Кто проверил',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='moderated_event_reviews',
    )

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Отзыв о мероприятии'
        verbose_name_plural = 'Отзывы о мероприятиях'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'status', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        """Возвращает строку вида «Автор → Мероприятие (оценка)»."""
        return f'{self.author_name} → {self.event} ({self.rating})'

    @property
    def is_anonymous(self):
        """Оставлен ли отзыв анонимным пользователем."""
        return self.user_id is None

    @property
    def is_published(self):
        """Отзыв прошёл модерацию и отображается публично."""
        return self.status == self.Status.PUBLISHED

    def mark_published(self, *, by=None, save=True):
        """Публикует отзыв после модерации."""
        self.status = self.Status.PUBLISHED
        self.moderated_at = timezone.now()
        if by is not None and getattr(by, 'is_authenticated', False):
            self.moderated_by = by
        if save:
            self.save(update_fields=[
                'status',
                'moderated_at',
                'moderated_by',
                'updated_at',
            ])

    def mark_rejected(self, *, by=None, reason='', save=True):
        """Отклоняет отзыв, сохраняя причину и модератора."""
        self.status = self.Status.REJECTED
        self.moderated_at = timezone.now()
        if reason:
            self.moderation_note = reason
        if by is not None and getattr(by, 'is_authenticated', False):
            self.moderated_by = by
        if save:
            self.save(update_fields=[
                'status',
                'moderated_at',
                'moderated_by',
                'moderation_note',
                'updated_at',
            ])
