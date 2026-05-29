from django.contrib import admin
from django.urls import path
from crm.views import company_dashboard, dashboard, users_settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('company/', company_dashboard, name='company_dashboard'),
    path('settings/users/', users_settings, name='users_settings'),
]
