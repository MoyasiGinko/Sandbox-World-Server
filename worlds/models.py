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
