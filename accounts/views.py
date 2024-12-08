import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render

from accounts.forms import UserLoginForm
from accounts.models import User

# Logging initialization
logger = logging.getLogger("django")


def login_user(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_username = form.cleaned_data["login_username"]
            login_password = form.cleaned_data["login_password"]
            try:
                user = User.objects.get(username=login_username)
            except User.DoesNotExist:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Username is invalid!",
                    extra_tags="alert-danger",
                )
                return redirect("login_user")

            user = authenticate(username=login_username, password=login_password)
            if user is not None:
                login(request, user)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "You have been logged in!",
                    extra_tags="success-subtle",
                )
                logger.info(f"'{user.username}' has logged in.")
                return redirect("task_list")
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Password is invalid!",
                    extra_tags="alert-danger",
                )
                return redirect("login_user")
        else:
            logger.error(form.errors)
            for error_list in form.errors.values():
                for error in error_list:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        error,
                        extra_tags="danger-subtle",
                    )
            return redirect("login_user")
    else:
        form = UserLoginForm()
        context = {"page_title": "Login", "form": form}
        return render(request, "accounts/login.html", context=context)


def logout_user(request):
    logout(request)
    messages.add_message(
        request,
        messages.SUCCESS,
        "You have been logged out!",
        extra_tags="alert-success",
    )
    return redirect("login_user")
