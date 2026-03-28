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
    path("users/<int:user_id>/stats", views.user_stats_api, name="users-stats-no-slash"),
    path("users/<int:user_id>/stats/", views.user_stats_api, name="users-stats"),
    path("leaderboard", views.leaderboard_api, name="leaderboard-no-slash"),
    path("leaderboard/", views.leaderboard_api, name="leaderboard"),
    path("matches/report", views.match_report_api, name="matches-report-no-slash"),
    path("matches/report/", views.match_report_api, name="matches-report"),
]
