from django.contrib.auth.models import User
from django.db import models


class PlayerStats(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player_stats")
	kills = models.IntegerField(default=0)
	deaths = models.IntegerField(default=0)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	playtime_seconds = models.IntegerField(default=0)
	matches_played = models.IntegerField(default=0)
	last_match = models.DateTimeField(null=True, blank=True)

	def to_public_dict(self) -> dict:
		deaths_value = self.deaths if self.deaths > 0 else 1
		kd_ratio = round(self.kills / deaths_value, 2)
		win_rate = round((self.wins / self.matches_played) * 100, 1) if self.matches_played > 0 else 0.0
		return {
			"user_id": self.user_id,
			"kills": self.kills,
			"deaths": self.deaths,
			"wins": self.wins,
			"losses": self.losses,
			"playtime_seconds": self.playtime_seconds,
			"matches_played": self.matches_played,
			"last_match": self.last_match.isoformat() if self.last_match else None,
			"kd_ratio": kd_ratio,
			"win_rate": win_rate,
			"playtime_hours": round(self.playtime_seconds / 3600, 1),
		}


class MatchHistory(models.Model):
	room_id = models.CharField(max_length=128)
	gamemode = models.CharField(max_length=64)
	winner = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="won_matches",
	)
	started_at = models.DateTimeField(null=True, blank=True)
	ended_at = models.DateTimeField(null=True, blank=True)
	duration_seconds = models.IntegerField(default=0)
	details = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
