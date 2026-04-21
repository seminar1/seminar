"""Представления приложения users: регистрация, вход, выход и админ-панель."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, View

from users.forms import LoginForm, RegisterForm, UserRoleForm
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
