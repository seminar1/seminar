"""URL-маршруты приложения users."""
from django.urls import path

from catalog.views import (
    AdminDirectionDeleteView,
    AdminDirectionsView,
    AdminDirectionUpdateView,
    AdminEventTypeDeleteView,
    AdminEventTypesView,
    AdminEventTypeUpdateView,
    AdminFeedbackMessageDetailView,
    AdminFeedbackMessagesView,
    AdminFeedbackTopicDeleteView,
    AdminFeedbackTopicsView,
    AdminFeedbackTopicUpdateView,
)
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
    path(
        'admin/directions/',
        AdminDirectionsView.as_view(),
        name='admin_directions',
    ),
    path(
        'admin/directions/<int:pk>/edit/',
        AdminDirectionUpdateView.as_view(),
        name='admin_direction_edit',
    ),
    path(
        'admin/directions/<int:pk>/delete/',
        AdminDirectionDeleteView.as_view(),
        name='admin_direction_delete',
    ),
    path(
        'admin/event-types/',
        AdminEventTypesView.as_view(),
        name='admin_event_types',
    ),
    path(
        'admin/event-types/<int:pk>/edit/',
        AdminEventTypeUpdateView.as_view(),
        name='admin_event_type_edit',
    ),
    path(
        'admin/event-types/<int:pk>/delete/',
        AdminEventTypeDeleteView.as_view(),
        name='admin_event_type_delete',
    ),
    path(
        'admin/feedback-topics/',
        AdminFeedbackTopicsView.as_view(),
        name='admin_feedback_topics',
    ),
    path(
        'admin/feedback-topics/<int:pk>/edit/',
        AdminFeedbackTopicUpdateView.as_view(),
        name='admin_feedback_topic_edit',
    ),
    path(
        'admin/feedback-topics/<int:pk>/delete/',
        AdminFeedbackTopicDeleteView.as_view(),
        name='admin_feedback_topic_delete',
    ),
    path(
        'admin/feedback/',
        AdminFeedbackMessagesView.as_view(),
        name='admin_feedback_messages',
    ),
    path(
        'admin/feedback/<int:pk>/',
        AdminFeedbackMessageDetailView.as_view(),
        name='admin_feedback_message_detail',
    ),
]
