"""
URL configuration for msal_cases project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.views.generic import RedirectView
from workqueue.msal_auth import login_begin, login_callback, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("workqueue.urls")),
    path("login/", login_begin, name="login"),
    path("auth/callback/", login_callback, name="auth_callback"),
    path("logout/", logout_view, name="logout"),
    path("home/", RedirectView.as_view(url="/")),
]