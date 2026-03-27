from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("worlds", "0002_gameserver"),
    ]

    operations = [
        migrations.CreateModel(
            name="RuntimeConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=128, unique=True)),
                ("value", models.TextField()),
                ("description", models.CharField(blank=True, default="", max_length=255)),
                ("is_public", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["key"],
            },
        ),
    ]
