"""Представления приложения users: регистрация, вход и выход."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View

from users.forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    """Страница регистрации нового пользователя.

    После успешной регистрации новому пользователю автоматически
    присваивается роль обычного пользователя (см. ``RegisterForm.save``)
    и выполняется вход в личный кабинет.
    """

    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:landing')

    def dispatch(self, request, *args, **kwargs):
        """Авторизованных пользователей перенаправляет на главную."""
        if request.user.is_authenticated:
            return redirect('catalog:landing')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Сохраняет пользователя и сразу же авторизует его."""
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            f'Добро пожаловать, {self.object.get_full_name() or self.object.username}!',
        )
        return response


class UserLoginView(LoginView):
    """Страница входа в личный кабинет."""

    form_class = LoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Возвращает URL, на который перенаправлять после входа."""
        next_url = self.get_redirect_url()
        return next_url or reverse_lazy('catalog:landing')

    def form_valid(self, form):
        """Добавляет приветственное сообщение после успешного входа."""
        response = super().form_valid(form)
        user = form.get_user()
        messages.success(
            self.request,
            f'С возвращением, {user.get_full_name() or user.username}!',
        )
        return response


class LogoutView(View):
    """Выход пользователя из сеанса."""

    def post(self, request, *args, **kwargs):
        """Завершает сессию и возвращает на главную страницу."""
        logout(request)
        messages.info(request, 'Вы вышли из аккаунта.')
        return redirect('catalog:landing')

    def get(self, request, *args, **kwargs):
        """Поддержка выхода по GET-запросу для удобства ссылок."""
        return self.post(request, *args, **kwargs)
