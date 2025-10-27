"""
URL configuration for student_project project.

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
from django.shortcuts import redirect

# Redirect root URL to login page
def root_redirect(request):
    return redirect('login')  # Make sure 'login' is the name of your login URL in users app

urlpatterns = [
    path('', root_redirect, name='root_redirect'),  # Root goes to login/signup
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Optional built-in auth
    path('clubs/', include('clubs.urls')),  # Club app URLs
    path('users/', include('users.urls')),  # Login/signup/dashboard URLs
]
