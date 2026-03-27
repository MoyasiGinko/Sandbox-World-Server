from django.urls import path

from . import views

urlpatterns = [
    path("client-config", views.client_config_api, name="client-config-no-slash"),
    path("client-config/", views.client_config_api, name="client-config"),
]
