from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from users.models import CustomUser

from ..models import Task, TaskSubmission


class TaskModelTestCase(TestCase):
    def setUp(self):
        # Create some test users
        self.user1 = CustomUser.objects.create_user(username="user1", password="pass")
        self.user2 = CustomUser.objects.create_user(username="user2", password="pass")
        self.user3 = CustomUser.objects.create_user(username="user3", password="pass")

        # Create a task and assign it to user1 and user2
        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            type="project",
            status="not_started",
            priority="high",
            assigned_by=self.user1,
            due_date=timezone.now()
            + timedelta(days=7),  # Add 7 days to the current time
        )
        self.task.assigned_to.set([self.user1, self.user2])
        self.task.save()

    def test_task_model_creation(self):
        # Verify Task is created
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "This is a test task")
        self.assertEqual(self.task.type, "project")
        self.assertEqual(self.task.status, "not_started")
        self.assertEqual(self.task.priority, "high")
        self.assertEqual(self.task.assigned_by, self.user1)

    def test_task_model_read(self):
        # Read Task and verify details
        task_fetched = Task.objects.get(id=self.task.id)
        self.assertEqual(task_fetched.title, "Test Task")
        self.assertEqual(task_fetched.description, "This is a test task")
        self.assertEqual(task_fetched.type, "project")
        self.assertEqual(task_fetched.status, "not_started")
        self.assertEqual(task_fetched.priority, "high")

    def test_task_model_update(self):
        # Update Task
        self.task.title = "Updated Task"
        self.task.description = "Updated description"
        self.task.status = "in_progress"
        self.task.priority = "medium"
        self.task.save()

        # Fetch updated Task from database
        updated_task = Task.objects.get(id=self.task.id)

        # Verify updates
        self.assertEqual(updated_task.title, "Updated Task")
        self.assertEqual(updated_task.description, "Updated description")
        self.assertEqual(updated_task.status, "in_progress")
        self.assertEqual(updated_task.priority, "medium")

    def test_task_model_delete(self):
        # Delete Task
        self.task.delete()

        # Verify Task is deleted
        self.assertEqual(Task.objects.count(), 0)

    def test_task_model_task_submissions(self):
        # Check that TaskSubmission instances are created for user1 and user2
        self.assertEqual(TaskSubmission.objects.filter(task=self.task).count(), 2)
        self.assertTrue(
            TaskSubmission.objects.filter(task=self.task, user=self.user1).exists()
        )
        self.assertTrue(
            TaskSubmission.objects.filter(task=self.task, user=self.user2).exists()
        )
        self.assertFalse(
            TaskSubmission.objects.filter(task=self.task, user=self.user3).exists()
        )
        # Check the details of a TaskSubmission
        submission1 = TaskSubmission.objects.get(task=self.task, user=self.user1)
        self.assertEqual(submission1.submitted, False)
        submission1.submitted = True
        self.assertEqual(submission1.submitted, True)
        self.assertEqual(submission1.task, self.task)
        self.assertEqual(submission1.user, self.user1)
