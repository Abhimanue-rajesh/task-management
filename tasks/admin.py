from django.contrib import admin

from .models import Activity, Task, TaskSubmission

admin.site.register(Task)
admin.site.register(Activity)
admin.site.register(TaskSubmission)
