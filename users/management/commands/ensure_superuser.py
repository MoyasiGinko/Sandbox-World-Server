import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Ensure a deploy-time superuser from DJANGO_SUPERUSER_* env vars exists and is usable."

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
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
            },
        )

        # Always enforce a deploy-known login state for the configured admin user.
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=["email", "is_staff", "is_superuser", "is_active", "password"])

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{username}' credentials and flags"))
