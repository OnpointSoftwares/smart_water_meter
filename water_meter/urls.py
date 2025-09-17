from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'water_meter'

# API URLs
api_urlpatterns = [
    path('data/', views.WaterUsageCreateView.as_view(), name='api-data-create'),
    path('data/list/', views.WaterUsageListView.as_view(), name='api-data-list'),
    path('devices/', views.DeviceListView.as_view(), name='api-devices'),
    path('alerts/', views.AlertListView.as_view(), name='api-alerts'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='api-dashboard-stats'),
]

# Frontend URLs
urlpatterns = [
    # API endpoints
    path('api/', include(api_urlpatterns)),
    
    # Frontend views
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('devices/', views.devices, name='devices'),
    path('analytics/', views.analytics, name='analytics'),
    path('alerts/', views.alerts, name='alerts'),
    path('billing/', views.billing, name='billing'),
]
