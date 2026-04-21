"""Миксины приложения users для контроля доступа к представлениям."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Разрешает доступ только пользователям с ролью администратора.

    Использует свойство ``User.is_administrator``, которое возвращает
    ``True`` для суперпользователей и учётных записей с ``role == ADMIN``.
    Неавторизованные пользователи отправляются на страницу входа, а
    авторизованные без нужных прав получают 403.
    """

    raise_exception = True

    def test_func(self):
        """Проверяет, что текущий пользователь — администратор."""
        user = self.request.user
        return user.is_authenticated and user.is_administrator


class CuratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Разрешает доступ кураторам и администраторам.

    Администратор по умолчанию обладает полными правами, поэтому ему
    также доступна кураторская панель управления. Обычные пользователи
    получают 403.
    """

    raise_exception = True

    def test_func(self):
        """Проверяет, что пользователь — куратор или администратор."""
        user = self.request.user
        return (
            user.is_authenticated
            and (user.is_curator or user.is_administrator)
        )
