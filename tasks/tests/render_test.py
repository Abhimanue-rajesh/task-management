from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projects.models import Project
from tasks.models import Task
from users.models import CustomUser, Role


class TestRender(TestCase):
    def setUp(self):
        # Set up a test Role
        self.role = Role.objects.create(type="MANAGER")
        # Set up a test user

        self.user = CustomUser.objects.create_user(
            username="testuser", password="password", role=self.role
        )
        # Log in the test user
        self.client.login(username="testuser", password="password")

        # Set up a test project
        self.project = Project.objects.create(
            title="Test Project",
            start_date="2024-09-01",
            time_line=199,
            quote_amount=1000,
            advance_amount=100,
        )

        # Set up a test task
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Task Description",
            type="project",
            status="not_started",
            priority="medium",
            assigned_by=self.user,
            project=self.project,
            due_date=timezone.now() + timezone.timedelta(days=7),
            all_submitted=False,
            approval_status=False,
        )

        # Add the user to the assigned_to ManyToMany field
        self.task.assigned_to.add(self.user)

    def test_task_list(self):
        url = reverse("task_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_list.html")

    def test_list_submitted_tasks(self):
        url = reverse("list_submitted_tasks")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/list_submitted_tasks.html")

    def test_list_approved_tasks(self):
        url = reverse("list_approved_tasks")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tasks/list_approved_tasks.html")

    def test_task_submission(self):
        task_id = self.task.id  # Use the ID of the task created in setUp
        url = reverse("task_submission", kwargs={"pk": task_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tasks/task_details.html")

    def test_task_detail(self):
        task_id = self.task.id
        url = reverse("task_detail", kwargs={"pk": task_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tasks/task_details.html")

    def test_update_task(self):
        task_id = self.task.id
        url = reverse("update_task", kwargs={"pk": task_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tasks/task_create_update.html")

    def test_create_task(self):
        url = reverse("create_task")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("tasks/task_create_update.html")
