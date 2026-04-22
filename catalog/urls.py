"""URL-маршруты приложения catalog."""
from django.urls import path, register_converter

from catalog.converters import UnicodeSlugConverter
from catalog.views import (
    AboutView,
    ContactsView,
    CuratorEventCreateView,
    CuratorEventsView,
    EventDetailView,
    EventRegisterView,
    EventRegistrationCancelView,
    EventsView,
    FaqView,
    FeedbackView,
    LandingView,
    MyRegistrationsView,
)

register_converter(UnicodeSlugConverter, 'uslug')

app_name = 'catalog'

urlpatterns = [
    path('', LandingView.as_view(), name='landing'),
    path('events/', EventsView.as_view(), name='events'),
    path(
        'events/<uslug:slug>/',
        EventDetailView.as_view(),
        name='event_detail',
    ),
    path(
        'events/<uslug:slug>/register/',
        EventRegisterView.as_view(),
        name='event_register',
    ),
    path(
        'registrations/<int:pk>/cancel/',
        EventRegistrationCancelView.as_view(),
        name='registration_cancel',
    ),
    path(
        'my/registrations/',
        MyRegistrationsView.as_view(),
        name='my_registrations',
    ),
    path('about/', AboutView.as_view(), name='about'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('contacts/', ContactsView.as_view(), name='contacts'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path(
        'curator/events/',
        CuratorEventsView.as_view(),
        name='curator_events',
    ),
    path(
        'curator/events/new/',
        CuratorEventCreateView.as_view(),
        name='curator_event_create',
    ),
]
