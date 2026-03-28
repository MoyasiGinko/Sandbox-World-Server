from django.contrib import admin

from users.models import MatchHistory, PlayerStats


@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ("user", "kills", "deaths", "wins", "losses", "matches_played", "last_match")
    search_fields = ("user__username", "user__email")


@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "room_id", "gamemode", "winner", "duration_seconds", "ended_at", "created_at")
    search_fields = ("room_id", "gamemode", "winner__username")
