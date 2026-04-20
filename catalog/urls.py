"""URL-маршруты приложения catalog."""
from django.urls import path

from catalog.views import AboutView, LandingView

app_name = 'catalog'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('about/', AboutView.as_view(), name='about'),
]
