from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from accounts.models import User


class Command(BaseCommand):
    help = "Populates the database with fake users"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Populating Users")
        fake = Faker(["en_IN"])

        for _ in range(5):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = fake.user_name()
            email = fake.email()
            phone_number = fake.phone_number()
            address = fake.address()

            User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password="pass",
                phone_number=phone_number,
                address=address,
            )

        check_users = User.objects.all().count()
        self.stdout.write(self.style.SUCCESS(f"Number of Users: {check_users}"))
