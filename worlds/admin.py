from django.contrib import admin

from .models import GameServer, RuntimeConfig, World

@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "author", "featured", "downloads", "reports")
	search_fields = ("name", "author")


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


@admin.register(RuntimeConfig)
class RuntimeConfigAdmin(admin.ModelAdmin):
	list_display = ("key", "value", "is_public", "updated_at")
	search_fields = ("key", "value", "description")
	list_filter = ("is_public",)
