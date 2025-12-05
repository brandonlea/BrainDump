"""
URL configuration for the BrainDump project.
Includes all app URLs and authentication URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Posts app URLs
    path('', include('posts.urls')),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
]
