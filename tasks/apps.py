from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        # Importing signals to ensure they are connected
        import tasks.signals  # noqa: F401 - Ignore Flake8 warning for unused import
