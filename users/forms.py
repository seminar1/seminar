"""Формы приложения users: регистрация и вход пользователей.

Формы используют кастомную модель ``users.User`` и применяют единый
визуальный стиль сайта: все поля получают CSS-класс ``auth-form__input``.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class StyledFormMixin:
    """Добавляет CSS-классы и плейсхолдеры ко всем полям формы."""

    default_css_class = 'auth-form__input'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (
                f'{existing} {self.default_css_class}'.strip()
            )
            widget.attrs.setdefault('autocomplete', 'off')
            if not widget.attrs.get('placeholder'):
                widget.attrs['placeholder'] = field.label or name


class RegisterForm(StyledFormMixin, UserCreationForm):
    """Форма регистрации нового пользователя каталога.

    При сохранении пользователю автоматически присваивается роль
    ``User.Role.USER`` (обычный пользователь). Роль администратора
    выдаётся исключительно через management-команду ``createsuperuser``.
    """

    first_name = forms.CharField(
        label='Имя',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Иван'}),
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Иванов'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}),
    )

    class Meta:
        model = User
        fields = (
            'last_name',
            'first_name',
            'username',
            'email',
            'password1',
            'password2',
        )
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логин'}),
        }

    def clean_email(self):
        """Проверяет уникальность e-mail среди зарегистрированных."""
        email = self.cleaned_data.get('email', '').strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Пользователь с таким e-mail уже зарегистрирован.'
            )
        return email

    def save(self, commit=True):
        """Сохраняет пользователя с ролью обычного пользователя."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = User.Role.USER
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    """Форма входа по логину и паролю."""

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'Ваш логин'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )
