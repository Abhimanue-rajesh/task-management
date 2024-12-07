import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.models import User

from .forms import CreateUpdateTask, SubmitTaskForm
from .models import Activity, Task, TaskSubmission

logger = logging.getLogger("django")


class TaskList(LoginRequiredMixin, ListView):
    paginate_by = 10
    ordering = ["id"]
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "all_tasks"
    extra_context = {"page_title": "All Tasks"}

    def get_queryset(self):
        queryset = Task.objects.all()
        type_filter = self.request.GET.get("type")
        priority_filter = self.request.GET.get("priority")
        status_filter = self.request.GET.get("status")
        assigned_to_filter = self.request.GET.getlist("assigned_to")
        due_date_sort = self.request.GET.get("due_date_sort")

        if type_filter:
            queryset = queryset.filter(type=type_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if assigned_to_filter and any(assigned_to_filter):
            queryset = queryset.filter(assigned_to__in=assigned_to_filter)
        if due_date_sort == "asc":
            queryset = queryset.order_by("due_date")
        elif due_date_sort == "desc":
            queryset = queryset.order_by("-due_date")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_choices"] = Task.TYPE
        context["priority_choices"] = Task.PRIORITY
        context["status_choices"] = Task.STATUS
        context["assigned_to_choices"] = (
            User.objects.filter(AssignedUsers__isnull=False)
            .distinct()
            .values_list("id", "username")
        )

        context["due_date_sort_options"] = [
            ("asc", "Due Date (Low to High)"),
            ("desc", "Due Date (High to Low)"),
        ]
        context["selected_assigned_to"] = self.request.GET.getlist("assigned_to")
        context["status_choices"] = [
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
        ]

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_details.html"
    context_object_name = "task"
    extra_context = {"page_title": "Task Details"}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        task = self.object
        context["activities"] = self.object.activities.all()
        context["form"] = SubmitTaskForm()
        is_assigned = task.assigned_to.filter(id=user.id).exists()
        user_submission = task.submissions.filter(user=user).first()
        has_submitted = user_submission.submitted if user_submission else False
        all_submitted = all(
            TaskSubmission.objects.filter(
                task=task, user=assigned_user, submitted=True
            ).exists()
            for assigned_user in task.assigned_to.all()
        )
        # Check if all users assigned to the task have submitted their work
        # This code does the following:
        # 1. Iterates over all users assigned to the task (task.assigned_to.all())
        # 2. For each assigned user, checks if there's a TaskSubmission that is:
        #    - associated with this task
        #    - created by this user
        #    - marked as submitted (submitted=True)
        # 3. The all() function returns True only if every assigned user has a submission
        #    that meets these criteria, otherwise it returns False
        # This can be used to determine if a task is fully complete or still in progress
        context.update(
            {
                "activities": task.activities.all(),
                "form": SubmitTaskForm(),
                "is_assigned": is_assigned,
                "has_submitted": has_submitted,
                "all_submitted": all_submitted,
            }
        )
        return context


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = CreateUpdateTask
    template_name = "tasks/task_create_update.html"
    extra_context = {"page_title": "Create Task"}

    role_hierarchy = {
        "C_SUITE": ["C_SUITE", "MANAGER", "EMPLOYEE", "TRAINEE"],
        "MANAGER": ["MANAGER", "EMPLOYEE", "TRAINEE"],
        "EMPLOYEE": ["EMPLOYEE", "TRAINEE"],
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.role.type
        assignable_roles = self.role_hierarchy.get(user_role, [])
        if user_role != "TRAINEE":
            users = User.objects.filter(role__type__in=assignable_roles)
            context["users"] = users

        return context

    def get_initial(self):
        initial = super().get_initial()

        # Get the project_id from the URL kwargs or query parameters
        project_id = self.kwargs.get("project_pk") or self.request.GET.get("project_pk")

        if project_id:
            initial["project"] = project_id  # Prefill the project field
            initial["type"] = "project"

        return initial

    def get_success_url(self):
        return reverse("task_detail", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        current_user = self.request.user
        form.instance.assigned_by = current_user

        # Save the form to create the Task object and get the ID
        response = super().form_valid(form)

        Activity.objects.create(
            task=self.object,
            description=f"Task created by {self.object.assigned_by} at {self.object.created_at}",
        )

        if current_user.role.type == "TRAINEE":
            form.instance.assigned_to.add(current_user)
        else:
            assigned_usernames = self.request.POST.get("assigned_to", "").split(", ")
            invalid_usernames = []

            for username in assigned_usernames:
                username = username.strip()
                if username:
                    try:
                        user = User.objects.get(username=username)
                        form.instance.assigned_to.add(user)
                    except User.DoesNotExist:
                        invalid_usernames.append(username)

            if invalid_usernames:
                messages.error(
                    self.request,
                    f"The following users do not exist: {', '.join(invalid_usernames)}",
                )

        return response

    def form_invalid(self, form):
        logger.error(form.errors)
        for error_list in form.errors.values():
            for error in error_list:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    error,
                    extra_tags="danger-subtle",
                )
        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = CreateUpdateTask
    template_name = "tasks/task_create_update.html"
    extra_context = {"page_title": "Update Task"}

    role_hierarchy = {
        "C_SUITE": ["C_SUITE", "MANAGER", "EMPLOYEE", "TRAINEE"],
        "MANAGER": ["MANAGER", "EMPLOYEE", "TRAINEE"],
        "EMPLOYEE": ["EMPLOYEE", "TRAINEE"],
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.role.type
        assignable_roles = self.role_hierarchy.get(user_role, [])
        if user_role != "TRAINEE":
            users = User.objects.filter(role__type__in=assignable_roles)
            context["users"] = users
            context["assigned_users"] = (
                self.object.assigned_to.all()
            )  # Add assigned users
        return context

    def get_success_url(self):
        return reverse("task_detail", kwargs={"pk": self.object.id})

    def get_initial(self):
        initial = super().get_initial()

        # Get the project_id from the URL kwargs or query parameters
        project_id = self.kwargs.get("project_pk") or self.request.GET.get("project_pk")

        if project_id:
            initial["project"] = project_id  # Prefill the project field
            initial["type"] = "project"

        return initial

    def form_valid(self, form):
        current_user = self.request.user

        # Save the form to update the Task object
        response = super().form_valid(form)

        # Clear existing assignments
        form.instance.assigned_to.clear()

        if current_user.role.type == "TRAINEE":
            form.instance.assigned_to.add(current_user)
        else:
            assigned_usernames = self.request.POST.get("assigned_to", "").split(", ")
            invalid_usernames = []

            for username in assigned_usernames:
                username = username.strip()
                if username:
                    try:
                        user = User.objects.get(username=username)
                        form.instance.assigned_to.add(user)
                    except User.DoesNotExist:
                        invalid_usernames.append(username)

            if invalid_usernames:
                messages.error(
                    self.request,
                    f"The following users do not exist: {', '.join(invalid_usernames)}",
                )

        return response

    def form_invalid(self, form):
        logger.error(form.errors)
        for error_list in form.errors.values():
            for error in error_list:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    error,
                    extra_tags="danger-subtle",
                )
        return super().form_invalid(form)


@login_required
def update_task_status(request, pk):
    to_update_status_task = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        incoming_status_data = request.POST.get("status_select")
        to_update_status_task.status = incoming_status_data
        to_update_status_task.save()

        messages.add_message(
            request,
            messages.SUCCESS,
            "Task status updated successfully!",
            extra_tags="alert-success",
        )

        Activity.objects.create(
            task=to_update_status_task,
            description=f"Status Updated by {request.user} to {to_update_status_task.get_status_display()}",
        )

        return redirect("task_detail", pk=pk)


@login_required
def delete_task(request, pk):
    to_delete_task = Task.objects.get(id=pk)
    to_delete_task.delete()
    messages.add_message(
        request,
        messages.SUCCESS,
        "Task has been deleted successfully!",
        extra_tags="alert-success",
    )

    return redirect("task_list")


class SubmittedTasksList(LoginRequiredMixin, ListView):
    paginate_by = 10
    ordering = ["id"]
    model = Task
    template_name = "tasks/list_submitted_tasks.html"
    context_object_name = "submitted_task"

    def get_queryset(self):
        return Task.objects.filter(all_submitted=True, approval_status=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "List Submitted Tasks"
        return context


class ApprovedTaskList(LoginRequiredMixin, ListView):
    paginate_by = 10
    ordering = ["id"]
    model = Task
    template_name = "tasks/list_approved_tasks.html"
    context_object_name = "approved_tasks"

    def get_queryset(self):
        return Task.objects.filter(approval_status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "List Approved Tasks"
        return context


@login_required
def approve_task(request, pk):
    to_approve_task = get_object_or_404(Task, id=pk)
    to_approve_task.approval_status = True
    to_approve_task.status = "completed"
    to_approve_task.save()
    Activity.objects.create(
        task=to_approve_task,
        description=f"Task has been approved by {request.user}",
    )
    logger.info(f"'{to_approve_task.title}' has been approved")
    messages.add_message(
        request,
        messages.SUCCESS,
        "Task approved successfully!",
        extra_tags="alert-success",
    )
    return redirect("list_approved_tasks")


def task_submission(request, pk):
    task = get_object_or_404(Task, id=pk)
    if request.method == "POST":
        form = SubmitTaskForm(request.POST)
        if form.is_valid():
            # TODO Need to handle this exception more efficiently.
            try:
                task_instance = TaskSubmission.objects.get(
                    task=task,
                    user=request.user,
                )
            except Exception as error:
                logger.error(f"Multiple Values for Submission - {error}")
                messages.error(
                    request,
                    "Some Unknown error occurred please retry again later!.",
                    extra_tags="alert-danger",
                )
                return redirect("task_detail", pk=task.id)

            task_instance.remarks = form.cleaned_data["remarks"]
            task_instance.submitted = True
            task_instance.save()
            Activity.objects.create(
                task=task,
                description=f"Task has been submitted by {request.user} with the remark - {task_instance.remarks}",
            )
            messages.success(
                request, "Task submitted successfully!", extra_tags="alert-success"
            )
            return redirect("task_detail", pk=task.id)
        else:
            messages.error(
                request,
                "Form is not valid. Please correct the errors.",
                extra_tags="alert-danger",
            )
    else:
        form = SubmitTaskForm()
    context = {"form": form, "task": task}
    return render(request, "tasks/task_details.html", context)
