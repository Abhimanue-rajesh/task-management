import logging

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from accounts.models import User
from tasks.models import Activity, Task, TaskSubmission

logger = logging.getLogger("django")


@receiver(m2m_changed, sender=Task.assigned_to.through)
def create_task_submissions(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        # Only create submissions for newly added users
        new_users = instance.assigned_to.filter(pk__in=pk_set)

        for user in new_users:
            submission, created = TaskSubmission.objects.get_or_create(
                task=instance, user=user
            )
            if created:
                logger.info(f"TaskSubmission instance created for {user}")


@receiver(m2m_changed, sender=Task.assigned_to.through)
def manage_task_submissions(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        # Create TaskSubmission instances for newly added users
        new_users = instance.assigned_to.filter(pk__in=pk_set)
        for user in new_users:
            submission, created = TaskSubmission.objects.get_or_create(
                task=instance, user=user
            )
            if created:
                logger.info(f"TaskSubmission instance created for {user}")

    elif action == "post_remove":
        # Remove TaskSubmission instances for removed users
        removed_users = User.objects.filter(pk__in=pk_set)
        for user in removed_users:
            deleted_count, _ = TaskSubmission.objects.filter(
                task=instance, user=user
            ).delete()
            if deleted_count > 0:
                logger.info(f"TaskSubmission instance deleted for {user}")


@receiver(post_save, sender=TaskSubmission)
def register_submit_activity(sender, instance, created, **kwargs):
    # Check if the instance is being updated, not created
    if not created:
        # Check if 'submitted' has changed and is now True
        if (
            instance.submitted
            and instance.submitted
            != TaskSubmission.objects.get(pk=instance.pk).submitted
        ):
            Activity.objects.create(
                task=instance.task,
                description=f"{instance.user} has submitted the task.",
            )


@receiver(post_save, sender=TaskSubmission)
def task_submission_updated(sender, instance, created, **kwargs):
    if not created:
        # Get all TaskSubmission instances for the same task
        task_submissions = TaskSubmission.objects.filter(task=instance.task)

        # Check if all submissions are marked as submitted
        all_submitted = all(submission.submitted for submission in task_submissions)

        if all_submitted:
            # Logic to handle when all submissions are submitted
            # print(f'All submissions for task "{instance.task.title}" are submitted.')

            instance.task.all_submitted = True
            instance.task.status = "waiting_for_approval"
            instance.task.save()
            Activity.objects.create(
                task=instance.task,
                description=f"All submissions for task {instance.task.title} are submitted. Waiting for Approval",
            )

        else:
            # If not all submissions are submitted, ensure the task's all_submitted field is False
            if instance.task.all_submitted:
                instance.task.all_submitted = False
                instance.task.save()
