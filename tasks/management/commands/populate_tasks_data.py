from django.core.management.base import BaseCommand
from faker import Faker

from tasks.models import Task
from users.models import CustomUser


class Command(BaseCommand):
    help = "Populate tasks with fake data"

    def handle(self, *args, **kwargs):
        fake = Faker("en_IN")

        task_creation_user_input = int(input("Enter the number of tasks"))
        assigned_by_user = CustomUser.objects.first()

        future_date = fake.date_time_between(start_date="now", end_date="+30d")

        for _ in range(task_creation_user_input):
            task = Task.objects.create(
                title=fake.text(max_nb_chars=20),
                description=fake.texts(max_nb_chars=100),
                type="project",
                status="progress",
                priority="high",
                due_date=future_date,
                assigned_by=assigned_by_user,
            )

            assigned_to_users = CustomUser.objects.order_by("?")[:2]
            task.assigned_to.set(assigned_to_users)

        task_count = Task.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Number of Tasks created: {task_count}"))
