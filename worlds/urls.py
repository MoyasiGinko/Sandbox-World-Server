from django.urls import path

from . import views

urlpatterns = [
    path('', views.worlds_api, name='worlds-api'),
]
