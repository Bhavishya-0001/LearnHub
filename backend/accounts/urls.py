from django.urls import path
from .views import (
    RegisterView,
    CustomLoginView,
    CustomTokenRefreshView,
    LogoutView,
    CurrentUserView,
    ProfileView,
)

urlpatterns = [
    # Auth endpoints
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", CustomLoginView.as_view(), name="auth-login"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),

    # Profile endpoints
    path("profile/", ProfileView.as_view(), name="user-profile"),
]
