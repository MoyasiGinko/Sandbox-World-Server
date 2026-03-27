from django.contrib import admin

from .models import World

@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "author", "featured", "downloads", "reports")
	search_fields = ("name", "author")
