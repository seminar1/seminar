"""URL-маршруты приложения catalog."""
from django.urls import path, register_converter

from catalog.converters import UnicodeSlugConverter
from catalog.views import (
    AboutView,
    BenefitsView,
    ContactsView,
    CuratorDirectionDeleteView,
    CuratorDirectionsView,
    CuratorDirectionUpdateView,
    CuratorEventCreateView,
    CuratorEventsView,
    CuratorEventTypeDeleteView,
    CuratorEventTypesView,
    CuratorEventTypeUpdateView,
    CuratorRegistrationDetailView,
    CuratorRegistrationsView,
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
    path('benefits/', BenefitsView.as_view(), name='benefits'),
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
    path(
        'curator/registrations/',
        CuratorRegistrationsView.as_view(),
        name='curator_registrations',
    ),
    path(
        'curator/registrations/<int:pk>/',
        CuratorRegistrationDetailView.as_view(),
        name='curator_registration_detail',
    ),
    path(
        'curator/directions/',
        CuratorDirectionsView.as_view(),
        name='curator_directions',
    ),
    path(
        'curator/directions/<int:pk>/edit/',
        CuratorDirectionUpdateView.as_view(),
        name='curator_direction_edit',
    ),
    path(
        'curator/directions/<int:pk>/delete/',
        CuratorDirectionDeleteView.as_view(),
        name='curator_direction_delete',
    ),
    path(
        'curator/event-types/',
        CuratorEventTypesView.as_view(),
        name='curator_event_types',
    ),
    path(
        'curator/event-types/<int:pk>/edit/',
        CuratorEventTypeUpdateView.as_view(),
        name='curator_event_type_edit',
    ),
    path(
        'curator/event-types/<int:pk>/delete/',
        CuratorEventTypeDeleteView.as_view(),
        name='curator_event_type_delete',
    ),
]
