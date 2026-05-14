"""Django admin registrations for catalog models."""
from django.contrib import admin

from catalog.models import EventRegistrationStatusHistory


@admin.register(EventRegistrationStatusHistory)
class EventRegistrationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
    )
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = (
        'registration__user__username',
        'registration__event__title',
        'changed_by__username',
    )
    readonly_fields = (
        'registration',
        'old_status',
        'new_status',
        'changed_by',
        'changed_at',
    )
