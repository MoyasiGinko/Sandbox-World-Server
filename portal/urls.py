from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="portal-dashboard"),
    path("dashboard/", views.dashboard, name="portal-dashboard-alt"),
    path("api/auth/", views.auth_page, name="portal-auth"),
    path("api/users/", views.users_page, name="portal-users"),
    path("api/worlds/", views.worlds_page, name="portal-worlds"),
    path("api/servers/", views.servers_page, name="portal-servers"),
    path("api/config/", views.config_page, name="portal-config"),
]
