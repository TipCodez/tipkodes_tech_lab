import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME") or os.environ.get("ADMIN_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL") or os.environ.get("ADMIN_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD") or os.environ.get("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Skipping superuser setup. Set DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD to enable it."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        if created or password:
            user.set_password(password)
            changed = True

        if changed:
            user.save()

        message = "Created superuser" if created else "Updated superuser"
        self.stdout.write(self.style.SUCCESS(f"{message}: {username}"))
