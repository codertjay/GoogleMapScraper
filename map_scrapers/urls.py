from django.urls import path
from . import views
from .views import DownloadUserCSVView, DownloadAllCSVView, SearchWithCSV, get_csv_sample

urlpatterns = [
    path('', views.map_view, name='map'),
    path('search/', views.search_api, name='search_api'),
    path('place_detail/', views.place_detail, name='place_detail'),
    path('autocomplete/', views.autocomplete_api, name='autocomplete'),
    path('history/', views.HistoryListView.as_view(), name='history_list'),
    path('admin_history/', views.AdminHistoryListView.as_view(), name='admin_history'),
    path('history_update/', views.HistoryUpdateView.as_view(), name='history_update'),
    path('history_delete/', views.HistoryDeleteView.as_view(), name='history_delete'),
    path('history_download/', DownloadUserCSVView.as_view(), name='csv_download'),
    path('history_download_all/', DownloadAllCSVView.as_view(), name='csv_all_download'),
    path('search_with_csv/', SearchWithCSV.as_view(), name='search_with_csv'),
    path('csv_sample/', get_csv_sample, name='csv_sample'),

]