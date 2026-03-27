from django.urls import include, path
from worlds import views as world_views

urlpatterns = [
    path('', include('users.urls')),
    path('worlds', world_views.worlds_api, name='worlds-api-no-slash'),
    path('worlds/', world_views.worlds_api, name='worlds-api'),
    path('', include('servers.urls')),
    path('', include('config.urls')),
]
