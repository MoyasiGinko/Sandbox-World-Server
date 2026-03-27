from django.db import models


class World(models.Model):
	name = models.CharField(max_length=255)
	featured = models.BooleanField(default=False)
	date = models.DateField(auto_now_add=True)
	downloads = models.PositiveIntegerField(default=0)
	version = models.CharField(max_length=64, default="0")
	author = models.CharField(max_length=255, default="unknown")
	image = models.TextField(blank=True)  # base64 preview
	tbw = models.TextField()
	reports = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date", "-id"]

	def __str__(self) -> str:  # pragma: no cover - debug helper
		return f"{self.name} (#{self.pk})"

	def to_public_dict(self) -> dict:
		return {
			"id": self.pk,
			"name": self.name,
			"featured": 1 if self.featured else 0,
			"date": self.date.strftime("%Y-%m-%d"),
			"downloads": self.downloads,
			"version": self.version,
			"author": self.author,
			"image": self.image,
		}


class GameServer(models.Model):
	server_id = models.CharField(max_length=64, unique=True)
	name = models.CharField(max_length=255)
	region = models.CharField(max_length=64, default="global")
	api_url = models.URLField()
	ws_url = models.URLField()
	is_public = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)
	current_players = models.PositiveIntegerField(default=0)
	max_players = models.PositiveIntegerField(default=64)
	build_version = models.CharField(max_length=64, blank=True, default="")
	last_heartbeat = models.DateTimeField(auto_now=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name", "server_id"]

	def __str__(self) -> str:  # pragma: no cover - debug helper
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
