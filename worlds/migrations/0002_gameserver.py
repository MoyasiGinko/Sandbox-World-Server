from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("worlds", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GameServer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("server_id", models.CharField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("region", models.CharField(default="global", max_length=64)),
                ("api_url", models.URLField()),
                ("ws_url", models.URLField()),
                ("is_public", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
                ("current_players", models.PositiveIntegerField(default=0)),
                ("max_players", models.PositiveIntegerField(default=64)),
                ("build_version", models.CharField(blank=True, default="", max_length=64)),
                ("last_heartbeat", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name", "server_id"],
            },
        ),
    ]
