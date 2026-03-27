import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from DJANGO_SUPERUSER_* env vars if missing."

    def handle(self, *args, **options):
        username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "admin@example.com").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or ""

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser creation: set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD"
                )
            )
            return

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists"))
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
