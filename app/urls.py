"""Корневая конфигурация URL-маршрутов проекта."""
from urllib.parse import urljoin

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

# Браузеры часто запрашивают /favicon.ico в корне; редирект на реальный ICO в static.
urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=urljoin(settings.STATIC_URL, "favicon.ico"),
            permanent=False,
        ),
    ),
    path("admin/", admin.site.urls),
    path('accounts/', include('users.urls', namespace='users')),
    path('', include('catalog.urls', namespace='catalog')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
