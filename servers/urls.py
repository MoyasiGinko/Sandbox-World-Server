from django.urls import path

from . import views

urlpatterns = [
    path("game-servers", views.game_servers_api, name="game-servers-api-no-slash"),
    path("game-servers/", views.game_servers_api, name="game-servers-api"),
    path("game-servers/<str:server_id>/heartbeat", views.game_server_heartbeat_api, name="game-server-heartbeat-no-slash"),
    path("game-servers/<str:server_id>/heartbeat/", views.game_server_heartbeat_api, name="game-server-heartbeat"),
]
