from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GameServerRoomCapacity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("server_id", models.CharField(max_length=64, unique=True)),
                ("max_rooms", models.PositiveIntegerField(default=100)),
                ("current_rooms", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "servers_room_capacity",
                "ordering": ["server_id"],
            },
        ),
    ]
