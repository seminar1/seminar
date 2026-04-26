"""Формы приложения catalog: управление мероприятиями и справочниками."""
from django import forms
from django.core.exceptions import ValidationError

from catalog.models import (
    Direction,
    Event,
    EventRegistration,
    EventType,
    FeedbackMessage,
    FeedbackTopic,
)


class DirectionForm(forms.ModelForm):
    """Форма создания и редактирования научного направления."""

    default_css_class = 'curator-form__input'

    class Meta:
        model = Direction
        fields = ('title', 'icon', 'description', 'is_active')
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Например, «Информационные технологии»'}
            ),
            'icon': forms.TextInput(
                attrs={'placeholder': 'bi-cpu'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Краткое описание направления'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs.setdefault('class', 'curator-form__checkbox')
                continue
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )


class EventTypeForm(forms.ModelForm):
    """Форма создания и редактирования типа мероприятия."""

    default_css_class = 'curator-form__input'

    class Meta:
        model = EventType
        fields = ('title', 'icon', 'is_active')
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Например, «Конференция»'}
            ),
            'icon': forms.TextInput(
                attrs={'placeholder': 'bi-people'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs.setdefault('class', 'curator-form__checkbox')
                continue
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )


class EventForm(forms.ModelForm):
    """Форма создания и редактирования научного мероприятия.

    Используется кураторами и администраторами в кураторской панели.
    Организатор автоматически проставляется во view как текущий
    авторизованный пользователь.
    """

    default_css_class = 'curator-form__input'

    starts_at = forms.DateTimeField(
        label='Начало',
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    ends_at = forms.DateTimeField(
        label='Окончание',
        required=False,
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M',
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = (
            'title',
            'short_description',
            'description',
            'direction',
            'event_type',
            'event_format',
            'starts_at',
            'ends_at',
            'location',
            'online_url',
            'seats_total',
            'cover',
            'status',
            'is_featured',
        )
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Например, «Международная конференция ИИ-2026»'}
            ),
            'short_description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Короткий анонс для карточки в каталоге',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 8,
                    'placeholder': 'Программа, спикеры, условия участия',
                }
            ),
            'event_format': forms.Select(),
            'direction': forms.Select(),
            'event_type': forms.Select(),
            'status': forms.Select(),
            'location': forms.TextInput(
                attrs={'placeholder': 'г. Москва, 2-й Кожуховский пр-д, 12'}
            ),
            'online_url': forms.URLInput(
                attrs={'placeholder': 'https://meet.example.com/...'}
            ),
            'seats_total': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direction'].queryset = Direction.objects.filter(is_active=True)
        self.fields['event_type'].queryset = EventType.objects.filter(is_active=True)
        for name, field in self.fields.items():
            if name == 'is_featured':
                field.widget.attrs.setdefault('class', 'curator-form__checkbox')
                continue
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )

    def clean(self):
        """Проверяет согласованность полей формата и дат проведения."""
        cleaned = super().clean()
        event_format = cleaned.get('event_format')
        location = cleaned.get('location', '').strip()
        online_url = cleaned.get('online_url', '').strip()
        starts_at = cleaned.get('starts_at')
        ends_at = cleaned.get('ends_at')

        if event_format == Event.Format.OFFLINE and not location:
            self.add_error(
                'location',
                'Для очного формата укажите место проведения.',
            )
        if event_format == Event.Format.ONLINE and not online_url:
            self.add_error(
                'online_url',
                'Для дистанционного формата укажите ссылку на трансляцию.',
            )
        if event_format == Event.Format.HYBRID and not (location and online_url):
            if not location:
                self.add_error(
                    'location',
                    'Для гибридного формата укажите место проведения.',
                )
            if not online_url:
                self.add_error(
                    'online_url',
                    'Для гибридного формата укажите ссылку на трансляцию.',
                )

        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error(
                'ends_at',
                'Окончание должно быть позже начала мероприятия.',
            )

        return cleaned


class EventRegistrationForm(forms.ModelForm):
    """Форма подачи заявки на участие в мероприятии.

    Отображается в шаблоне подтверждения регистрации. Поля контактов
    инициализируются данными из профиля пользователя и становятся
    снимком заявки — редактирование профиля в будущем не влияет на
    поданную заявку.
    """

    default_css_class = 'reg-form__input'

    class Meta:
        model = EventRegistration
        fields = (
            'full_name',
            'email',
            'phone',
            'organization',
            'position',
            'note',
        )
        widgets = {
            'full_name': forms.TextInput(
                attrs={'placeholder': 'Иванов Иван Иванович', 'autocomplete': 'name'}
            ),
            'email': forms.EmailInput(
                attrs={'placeholder': 'ivanov@example.com', 'autocomplete': 'email'}
            ),
            'phone': forms.TextInput(
                attrs={'placeholder': '+7 (999) 000-00-00', 'autocomplete': 'tel'}
            ),
            'organization': forms.TextInput(
                attrs={'placeholder': 'МУИВ, факультет ИТ'}
            ),
            'position': forms.TextInput(
                attrs={'placeholder': 'Студент, преподаватель, научный сотрудник'}
            ),
            'note': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': (
                        'Дополнительная информация для организаторов '
                        '(необязательно).'
                    ),
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['full_name'].required = True
        self.fields['email'].required = True

        if user is not None and not self.is_bound and not self.instance.pk:
            self.fields['full_name'].initial = (
                user.get_full_name() or user.username
            )
            self.fields['email'].initial = user.email or ''
            self.fields['phone'].initial = getattr(user, 'phone', '') or ''
            self.fields['organization'].initial = (
                getattr(user, 'organization', '') or ''
            )
            self.fields['position'].initial = (
                getattr(user, 'position', '') or ''
            )

        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )


class FeedbackMessageForm(forms.ModelForm):
    """Публичная форма обратной связи.

    Доступна всем пользователям — как авторизованным, так и анонимным.
    Для авторизованных пользователей поля ФИО и email предварительно
    заполняются данными профиля. В момент отправки создаётся
    ``FeedbackMessage``, связанный с учётной записью (если пользователь
    авторизован), иначе — анонимное обращение.
    """

    default_css_class = 'feedback-form__input'

    consent_to_processing = forms.BooleanField(
        label=(
            'Я согласен(на) на обработку персональных данных '
            'в соответствии с политикой конфиденциальности.'
        ),
        required=True,
        error_messages={
            'required': (
                'Для отправки обращения необходимо согласие '
                'на обработку персональных данных.'
            ),
        },
    )
    subscribe_to_news = forms.BooleanField(
        label='Хочу получать новостную рассылку о научных мероприятиях.',
        required=False,
    )

    class Meta:
        model = FeedbackMessage
        fields = (
            'topic',
            'full_name',
            'email',
            'phone',
            'organization',
            'subject',
            'message',
            'attachment',
            'consent_to_processing',
            'subscribe_to_news',
        )
        widgets = {
            'topic': forms.Select(),
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'Как к вам обращаться',
                    'autocomplete': 'name',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'placeholder': 'you@example.com',
                    'autocomplete': 'email',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'placeholder': '+7 (999) 000-00-00',
                    'autocomplete': 'tel',
                }
            ),
            'organization': forms.TextInput(
                attrs={'placeholder': 'МУИВ, факультет / организация (необязательно)'}
            ),
            'subject': forms.TextInput(
                attrs={'placeholder': 'Кратко о сути обращения'}
            ),
            'message': forms.Textarea(
                attrs={
                    'rows': 6,
                    'placeholder': (
                        'Опишите ваш вопрос, предложение или '
                        'обратную связь как можно подробнее.'
                    ),
                }
            ),
            'attachment': forms.ClearableFileInput(
                attrs={'class': 'feedback-form__file', 'accept': '.pdf,.doc,.docx,.odt,.txt,.rtf,.png,.jpg,.jpeg,.gif,.webp,.zip'}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['topic'].queryset = FeedbackTopic.objects.filter(
            is_active=True
        )
        self.fields['topic'].empty_label = 'Выберите тему обращения'
        self.fields['topic'].required = False

        self.fields['full_name'].required = True
        self.fields['email'].required = True
        self.fields['message'].required = True
        self.fields['attachment'].required = False
        self.fields['attachment'].label = 'Прикрепить файл'

        if user is not None and user.is_authenticated and not self.is_bound:
            self.fields['full_name'].initial = (
                user.get_full_name() or user.username
            )
            self.fields['email'].initial = user.email or ''
            self.fields['phone'].initial = getattr(user, 'phone', '') or ''
            self.fields['organization'].initial = (
                getattr(user, 'organization', '') or ''
            )

        for name, field in self.fields.items():
            if name in ('consent_to_processing', 'subscribe_to_news'):
                field.widget.attrs.setdefault('class', 'feedback-form__checkbox')
                continue
            if name == 'attachment':
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (
                    f'{existing} {self.default_css_class}'.strip()
                )
                continue
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )

    def clean_attachment(self):
        """Ограничение размера вложения для защиты от злоупотреблений."""
        f = self.cleaned_data.get('attachment')
        if f:
            max_bytes = 5 * 1024 * 1024
            if f.size > max_bytes:
                raise ValidationError(
                    'Размер файла не должен превышать 5 МБ.',
                )
        return f

    def clean_message(self):
        """Проверяет, что сообщение содержит осмысленный текст."""
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise forms.ValidationError(
                'Сообщение слишком короткое. Опишите обращение подробнее '
                '(минимум 10 символов).'
            )
        return message


class FeedbackTopicForm(forms.ModelForm):
    """Форма создания и редактирования темы обращений (админ-панель)."""

    default_css_class = 'curator-form__input'

    class Meta:
        model = FeedbackTopic
        fields = ('title', 'icon', 'description', 'order', 'is_active')
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Например, «Вопрос по мероприятию»'}
            ),
            'icon': forms.TextInput(
                attrs={'placeholder': 'bi-chat-dots'}
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': (
                        'Необязательная подсказка, показываемая рядом '
                        'с пунктом списка.'
                    ),
                }
            ),
            'order': forms.NumberInput(attrs={'min': 0, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs.setdefault('class', 'curator-form__checkbox')
                continue
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )


class AdminFeedbackMessageStatusForm(forms.ModelForm):
    """Компактная форма изменения статуса обращения администратором.

    Используется на карточке обращения в админ-панели — содержит
    только поле статуса. Прочие служебные поля (комментарии,
    назначение ответственного) в интерфейсе не используются.
    """

    default_css_class = 'feedback-status-form__select'

    class Meta:
        model = FeedbackMessage
        fields = ('status',)
        widgets = {
            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )


class CuratorRegistrationStatusForm(forms.ModelForm):
    """Компактная форма изменения статуса регистрации куратором.

    Позволяет переключать заявку между статусами жизненного цикла
    (ожидание подтверждения → подтверждена → посетил(а) / не явился
    / отменена / лист ожидания). Дополнительно принимает необязательное
    поле ``cancellation_reason``, которое сохраняется только при выборе
    статуса «Отменена».
    """

    default_css_class = 'feedback-status-form__select'

    class Meta:
        model = EventRegistration
        fields = ('status', 'cancellation_reason')
        widgets = {
            'status': forms.Select(),
            'cancellation_reason': forms.Textarea(
                attrs={
                    'rows': 2,
                    'placeholder': 'Укажите причину отмены (необязательно)',
                    'class': 'curator-form__input',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cancellation_reason'].required = False
        status_widget = self.fields['status'].widget
        existing = status_widget.attrs.get('class', '')
        status_widget.attrs['class'] = (
            f'{existing} {self.default_css_class}'.strip()
        )
