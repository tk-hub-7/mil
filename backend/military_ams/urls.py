"""
URL configuration for military_ams project.
"""
from django.contrib import admin
from django.urls import path, include
from .views import api_root

urlpatterns = [
    path('', api_root, name='api_root'),  # Root endpoint
    path('admin/', admin.site.urls),
    path('api/v1/', include('assets.urls')),
]
