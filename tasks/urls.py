from django.urls import path

from .views import (
    ApprovedTaskList,
    SubmittedTasksList,
    TaskCreate,
    TaskDetail,
    TaskList,
    TaskUpdateView,
    approve_task,
    delete_task,
    task_submission,
    update_task_status,
)

urlpatterns = [
    path("", TaskList.as_view(), name="task_list"),
    path("task/detail/<int:pk>", TaskDetail.as_view(), name="task_detail"),
    path("create/task/", TaskCreate.as_view(), name="create_task"),
    path(
        "add/task/<int:project_pk>/", TaskCreate.as_view(), name="add_task_with_project"
    ),
    path("update/task/<int:pk>", TaskUpdateView.as_view(), name="update_task"),
    path("update/task/status/<int:pk>/", update_task_status, name="update_task_status"),
    path("delete/task/<int:pk>/", delete_task, name="delete_task"),
    path("approve/task/<int:pk>/", approve_task, name="approve_task"),
    path("list/submitted/", SubmittedTasksList.as_view(), name="list_submitted_tasks"),
    path("list/approved/", ApprovedTaskList.as_view(), name="list_approved_tasks"),
    path("task/submission/<int:pk>/", task_submission, name="task_submission"),
]
