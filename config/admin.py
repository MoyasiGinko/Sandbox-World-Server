from django.contrib import admin

from .models import RuntimeConfig


@admin.register(RuntimeConfig)
class RuntimeConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "is_public", "updated_at")
    search_fields = ("key", "value", "description")
    list_filter = ("is_public",)
