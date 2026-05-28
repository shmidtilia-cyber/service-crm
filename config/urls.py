from django.contrib import admin
from django.urls import path
from crm.views import company_dashboard, dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('company/', company_dashboard, name='company_dashboard'),
]
