from django.db import models
from django.core.validators import URLValidator


class GameServer(models.Model):
    server_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=64, default="global")
    api_url = models.URLField()
    ws_url = models.URLField(
        validators=[URLValidator(schemes=["http", "https", "ws", "wss"])],
    )
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    current_players = models.PositiveIntegerField(default=0)
    max_players = models.PositiveIntegerField(default=64)
    build_version = models.CharField(max_length=64, blank=True, default="")
    last_heartbeat = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "worlds_gameserver"
        ordering = ["name", "server_id"]
        managed = False

    def __str__(self) -> str:
        return f"{self.name} ({self.server_id})"

    def to_public_dict(self) -> dict:
        return {
            "id": self.server_id,
            "name": self.name,
            "region": self.region,
            "api_url": self.api_url,
            "ws_url": self.ws_url,
            "is_public": self.is_public,
            "is_active": self.is_active,
            "current_players": self.current_players,
            "max_players": self.max_players,
            "build_version": self.build_version,
            "last_heartbeat": self.last_heartbeat.isoformat(),
        }
