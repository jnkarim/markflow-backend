from django.core.management.base import BaseCommand

from apps.accounts.models import User


class Command(BaseCommand):
    help = "Create or refresh the MarkFlow demo account."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            email="demo@markflow.app",
            defaults={
                "first_name": "Julker Nayeen",
                "last_name": "Karim",
                "is_active": True,
            },
        )
        user.first_name = "Julker Nayeen"
        user.last_name = "Karim"
        user.is_active = True
        user.set_password("1234abcd")
        user.save(update_fields=[
            "first_name",
            "last_name",
            "is_active",
            "password",
        ])

        self.stdout.write(
            self.style.SUCCESS(
                "Demo account ready: demo@markflow.app / 1234abcd"
            )
        )
