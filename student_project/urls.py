
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Redirect root URL to login page
def root_redirect(request):
    return redirect('login')  # Make sure 'login' is defined in your users app URLs


urlpatterns = [
    # Default redirect (homepage → login)
    path('', root_redirect, name='root_redirect'),

    # Django admin
    path('admin/', admin.site.urls),

    # Built-in Django authentication (optional)
    path('accounts/', include('django.contrib.auth.urls')),

    # Your apps
    path('clubs/', include('clubs.urls')),   # Clubs app URLs
    path('users/', include('users.urls')),   # Users app URLs (login, signup, dashboards)
    path('api/', include('api.urls')),       # REST API endpoints

    # JWT Authentication endpoints for mobile / frontend
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),   # Login → returns access + refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh access token
]
