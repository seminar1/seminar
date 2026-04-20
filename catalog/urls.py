"""URL-маршруты приложения catalog."""
from django.urls import path

from catalog.views import LandingView

app_name = 'catalog'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
]
