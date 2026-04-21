"""URL-маршруты приложения users."""
from django.urls import path

from users.views import (
    AdminUserRoleUpdateView,
    AdminUsersView,
    LogoutView,
    RegisterView,
    UserLoginView,
)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/users/', AdminUsersView.as_view(), name='admin_users'),
    path(
        'admin/users/<int:pk>/role/',
        AdminUserRoleUpdateView.as_view(),
        name='admin_user_role',
    ),
]
