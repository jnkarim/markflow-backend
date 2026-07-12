from django.core.management.base import BaseCommand

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Create or refresh the MarkFlow demo account."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            email="demo@markflow.app",
            defaults={
                "first_name": "Alex",
                "last_name": "Doyle",
                "is_active": True,
            },
        )
        user.first_name = "Alex"
        user.last_name = "Doyle"
        user.is_active = True
        user.set_password("MarkFlow123!")
        user.save(update_fields=[
            "first_name",
            "last_name",
            "is_active",
            "password",
        ])

        self.stdout.write(
            self.style.SUCCESS(
                "Demo account ready: demo@markflow.app / MarkFlow123!"
            )
        )
