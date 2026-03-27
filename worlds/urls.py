from django.urls import path

from . import views

urlpatterns = [
    path('auth/register', views.auth_register_api, name='auth-register-no-slash'),
    path('auth/register/', views.auth_register_api, name='auth-register'),
    path('auth/login', views.auth_login_api, name='auth-login-no-slash'),
    path('auth/login/', views.auth_login_api, name='auth-login'),
    path('auth/verify', views.auth_verify_api, name='auth-verify-no-slash'),
    path('auth/verify/', views.auth_verify_api, name='auth-verify'),
    path('users/display-name', views.update_display_name_api, name='users-display-name-no-slash'),
    path('users/display-name/', views.update_display_name_api, name='users-display-name'),
    path('client-config', views.client_config_api, name='client-config-no-slash'),
    path('client-config/', views.client_config_api, name='client-config'),
    path('worlds', views.worlds_api, name='worlds-api-no-slash'),
    path('worlds/', views.worlds_api, name='worlds-api'),
    path('game-servers', views.game_servers_api, name='game-servers-api-no-slash'),
    path('game-servers/', views.game_servers_api, name='game-servers-api'),
    path('game-servers/<str:server_id>/heartbeat', views.game_server_heartbeat_api, name='game-server-heartbeat-no-slash'),
    path('game-servers/<str:server_id>/heartbeat/', views.game_server_heartbeat_api, name='game-server-heartbeat'),
]
