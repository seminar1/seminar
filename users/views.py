"""Представления приложения users: регистрация, вход, выход и админ-панель."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, View

from users.forms import (
    LoginForm,
    ProfileUpdateForm,
    RegisterForm,
    UserPasswordChangeForm,
    UserRoleForm,
)
from users.mixins import AdminRequiredMixin

User = get_user_model()


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


class SettingsView(LoginRequiredMixin, View):
    """Страница «Настройки» личного кабинета.

    Доступна всем авторизованным пользователям. Содержит две формы:

    1. ``ProfileUpdateForm`` — редактирование персональных данных
       (ФИО, e-mail, телефон, организация, должность).
    2. ``UserPasswordChangeForm`` — смена пароля с проверкой старого
       пароля и стандартной валидацией нового пароля.

    Какая именно форма обрабатывается, определяется скрытым полем
    ``form_name`` в POST-запросе: ``profile`` или ``password``.
    Остальная форма рендерится без изменений (pristine).
    """

    template_name = 'users/settings.html'
    login_url = reverse_lazy('users:login')

    def _build_context(self, profile_form, password_form, active_section='profile'):
        """Формирует общий контекст шаблона для GET и POST."""
        return {
            'profile_form': profile_form,
            'password_form': password_form,
            'active_section': active_section,
        }

    def get(self, request, *args, **kwargs):
        """Отображает формы профиля и смены пароля, предзаполненные данными."""
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = UserPasswordChangeForm(user=request.user)
        return render(
            request,
            self.template_name,
            self._build_context(profile_form, password_form),
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает одну из двух форм в зависимости от поля ``form_name``."""
        form_name = request.POST.get('form_name')

        if form_name == 'password':
            return self._handle_password(request)
        return self._handle_profile(request)

    def _handle_profile(self, request):
        """Валидирует и сохраняет данные профиля."""
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        password_form = UserPasswordChangeForm(user=request.user)

        if profile_form.is_valid():
            profile_form.save()
            messages.success(
                request,
                'Данные профиля успешно обновлены.',
            )
            return redirect('users:settings')

        messages.error(
            request,
            'Не удалось сохранить профиль: проверьте заполнение полей.',
        )
        return render(
            request,
            self.template_name,
            self._build_context(
                profile_form, password_form, active_section='profile'
            ),
        )

    def _handle_password(self, request):
        """Валидирует и сохраняет новый пароль, сохраняя сессию активной."""
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = UserPasswordChangeForm(
            user=request.user, data=request.POST
        )

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Пароль успешно изменён. Вы остаётесь в системе.',
            )
            return redirect('users:settings')

        messages.error(
            request,
            'Не удалось сменить пароль: проверьте введённые данные.',
        )
        return render(
            request,
            self.template_name,
            self._build_context(
                profile_form, password_form, active_section='password'
            ),
        )


class LogoutView(View):
    """Выход пользователя из сеанса."""

    def post(self, request, *args, **kwargs):
        """Завершает сессию и возвращает на главную страницу."""
        logout(request)
        return redirect('catalog:landing')

    def get(self, request, *args, **kwargs):
        """Поддержка выхода по GET-запросу для удобства ссылок."""
        return self.post(request, *args, **kwargs)


class AdminUsersView(AdminRequiredMixin, ListView):
    """Админ-панель: список пользователей с возможностью смены ролей."""

    model = User
    template_name = 'users/admin/users.html'
    context_object_name = 'users_list'
    paginate_by = 20

    def get_queryset(self):
        """Возвращает пользователей, отсортированных по дате регистрации."""
        queryset = User.objects.all().order_by('-date_joined')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        role = self.request.GET.get('role', '').strip()
        if role in dict(User.Role.choices):
            queryset = queryset.filter(role=role)
        return queryset

    def get_context_data(self, **kwargs):
        """Передаёт в шаблон справочники для фильтров и формы смены роли."""
        context = super().get_context_data(**kwargs)
        context['role_choices'] = User.Role.choices
        context['current_role'] = self.request.GET.get('role', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['total_count'] = User.objects.count()
        context['admins_count'] = User.objects.filter(
            Q(role=User.Role.ADMIN) | Q(is_superuser=True)
        ).distinct().count()
        context['curators_count'] = User.objects.filter(
            role=User.Role.CURATOR
        ).count()
        context['users_count'] = User.objects.filter(
            role=User.Role.USER
        ).count()
        return context


class AdminUserRoleUpdateView(AdminRequiredMixin, View):
    """Обработчик смены роли одного пользователя из списка."""

    http_method_names = ['post']

    def post(self, request, pk, *args, **kwargs):
        """Меняет роль пользователя, если это допустимо."""
        target = get_object_or_404(User, pk=pk)
        redirect_url = request.POST.get('next') or reverse('users:admin_users')

        if target.pk == request.user.pk:
            messages.error(
                request,
                'Нельзя изменить собственную роль из админ-панели.',
            )
            return HttpResponseRedirect(redirect_url)

        form = UserRoleForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Роль пользователя {target.username} обновлена: '
                f'{target.get_role_display()}.',
            )
        else:
            messages.error(
                request,
                'Не удалось обновить роль. Проверьте корректность данных.',
            )
        return HttpResponseRedirect(redirect_url)
