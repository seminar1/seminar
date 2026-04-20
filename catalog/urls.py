"""URL-маршруты приложения catalog."""
from django.urls import path

from catalog.views import (
    AboutView,
    ContactsView,
    EventsView,
    FaqView,
    LandingView,
)

app_name = 'catalog'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('events/', EventsView.as_view(), name='events'),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
]
