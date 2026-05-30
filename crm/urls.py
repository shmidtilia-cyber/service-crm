from django.urls import path

from .views import company_dashboard, dashboard, users_settings
from .finance_views import finance_dashboard
from .reports_views import reports_dashboard
from .settings_views import settings_dashboard
from .order_views import order_detail

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('company/', company_dashboard, name='company_dashboard'),
    path('finance/', finance_dashboard, name='finance_dashboard'),
    path('reports/', reports_dashboard, name='reports_dashboard'),
    path('settings/', settings_dashboard, name='settings_dashboard'),
    path('settings/users/', users_settings, name='users_settings'),
]
