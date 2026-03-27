from django.db import models


class RuntimeConfig(models.Model):
    key = models.CharField(max_length=128, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=255, blank=True, default="")
    is_public = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "worlds_runtimeconfig"
        ordering = ["key"]
        managed = False

    def __str__(self) -> str:
        return f"{self.key}={self.value}"
