"""Формы приложения catalog: управление мероприятиями и справочниками."""
from django import forms

from catalog.models import Direction, Event, EventType


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
