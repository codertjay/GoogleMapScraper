from decouple import config
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

admin_url = config('ADMIN_URL', default='map_scrape_admin_dont_url')
urlpatterns = [
    path(f'{admin_url}/', admin.site.urls, name='admin'),
    path('', include('map_scrapers.urls')),
    path('accounts/', include('allauth.urls')),
    # for maintenance mode
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
