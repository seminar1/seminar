"""URL-маршруты приложения users."""
from django.urls import path

from users.views import LogoutView, RegisterView, UserLoginView

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
