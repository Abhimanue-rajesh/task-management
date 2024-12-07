from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone

from tasks.models import Task
from users.models import CustomUser

# class TaskListViewTest(TestCase):

#     def setUp(self):
#         # Create a test user
#         self.user = CustomUser.objects.create_user(
#             username="testuser", email="testuser@example.com", password="testpassword"
#         )
#         self.url = reverse_lazy("task_list")

#     def test_login_required(self):
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 302)
#         self.assertIn("/?next=/tasks/list/", response.url)

#     def test_view_url_exists_at_desired_location(self):
#         self.client.login(username="testuser", password="testpassword")
#         response = self.client.get("/tasks/list/")  # Adjust to your actual URL
#         self.assertEqual(response.status_code, 200)

#     def test_view_uses_correct_template(self):
#         self.client.login(username="testuser", password="testpassword")
#         response = self.client.get(self.url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "tasks/task_list.html")

#     def test_context_data(self):
#         self.client.login(username="testuser", password="testpassword")
#         response = self.client.get(self.url)
#         self.assertTrue("all_tasks" in response.context)
#         self.assertTrue("page_title" in response.context)
#         self.assertEqual(response.context["page_title"], "All Tasks")


class TaskDetailViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            type="project",
            status="in_progress",
            priority="high",
            assigned_by=self.user,
            due_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.task.assigned_to.add(self.user)
        self.url = reverse_lazy("task_detail", kwargs={"pk": self.task.pk})

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/?next=/tasks/task/detail/1", response.url)
