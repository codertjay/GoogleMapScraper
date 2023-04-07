from django.contrib import admin

# Register your models here.
from map_scrapers.models import History


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'latitude', 'longitude', 'timestamp')
    list_filter = ('user', 'business_name', 'municipality')
    search_fields = ('business_name', 'municipality')


admin.site.register(History,HistoryAdmin)
