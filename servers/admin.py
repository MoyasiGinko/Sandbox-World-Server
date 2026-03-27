from django.contrib import admin

from .models import GameServer


@admin.register(GameServer)
class GameServerAdmin(admin.ModelAdmin):
    list_display = (
        "server_id",
        "name",
        "region",
        "is_public",
        "is_active",
        "current_players",
        "max_players",
        "last_heartbeat",
    )
    search_fields = ("server_id", "name", "region")
    list_filter = ("is_public", "is_active", "region")
