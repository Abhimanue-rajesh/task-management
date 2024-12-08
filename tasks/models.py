from django.db import models
from django.utils import timezone


class Activity(models.Model):
    task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="activities"
    )
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.task.title} - {self.description[:20]}"


class Task(models.Model):
    PRIORITY = [
        ("critical", "Critical"),
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    STATUS = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("terminated", "Terminated"),
        ("waiting_for_approval", "Waiting For Approval"),
        ("completed", "Completed"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=27, choices=STATUS, default="not_started")
    priority = models.CharField(max_length=27, choices=PRIORITY)

    assigned_by = models.ForeignKey(
        "accounts.User", blank=True, on_delete=models.SET_NULL, null=True
    )
    assigned_to = models.ManyToManyField(
        "accounts.User", blank=True, related_name="AssignedUsers"
    )

    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_date = models.DateField(auto_now=True)
    due_date = models.DateField(default=timezone.now)

    all_submitted = models.BooleanField(default=False)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approval_status = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_view_approved_tasks", "Can View Approved Tasks"),
            ("can_view_submitted_tasks", "Can View Submitted Tasks"),
        ]

    def assigned_to_names(self):
        return [user.username for user in self.assigned_to.all()]

    def __str__(self):
        return self.title

    def is_user_assigned_and_submitted(self, user):
        is_assigned = self.assigned_to.filter(id=user.id).exists()
        has_submitted = TaskSubmission.objects.filter(
            task=self, user=user, submitted=True
        ).exists()
        return is_assigned, has_submitted

    def get_user_submission(self, user):
        return self.submissions.filter(user=user).first()

    def time_left(self):
        if self.due_date and self.created_at:
            time_left = (self.due_date - self.created_at).days
            if time_left <= 0:
                return "Due Date is Over"
            return f"{time_left} days"
        return None


class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} -{self.task.title} {'Submitted' if self.submitted else 'Not Submitted'}"
