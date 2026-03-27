from django.urls import path

from . import views

urlpatterns = [
    path("auth/register", views.auth_register_api, name="auth-register-no-slash"),
    path("auth/register/", views.auth_register_api, name="auth-register"),
    path("auth/login", views.auth_login_api, name="auth-login-no-slash"),
    path("auth/login/", views.auth_login_api, name="auth-login"),
    path("auth/verify", views.auth_verify_api, name="auth-verify-no-slash"),
    path("auth/verify/", views.auth_verify_api, name="auth-verify"),
    path("users/display-name", views.update_display_name_api, name="users-display-name-no-slash"),
    path("users/display-name/", views.update_display_name_api, name="users-display-name"),
]
