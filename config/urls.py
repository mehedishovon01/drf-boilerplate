"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from config import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'api/{settings.API_VERSION}/user/', include('users.urls')),

    # Automatic URL routing using API.
    # Additionally, include login URLs for the browsable API.
    # This is the DRF default login-logout API
    path(f'api/{settings.API_VERSION}/browser/', include('rest_framework.urls', namespace='rest_framework'))
]
