"""URL-маршруты приложения users."""
from django.urls import path

from catalog.views import (
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
    SettingsView,
    UserLoginView,
)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('admin/users/', AdminUsersView.as_view(), name='admin_users'),
    path(
        'admin/users/<int:pk>/role/',
        AdminUserRoleUpdateView.as_view(),
        name='admin_user_role',
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
