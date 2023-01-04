from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# this mixin allows us to restrict users who have not logged in.
from django.urls import reverse_lazy
from .models import Task


class CustomLoginView(LoginView):
    """Class to handle and render the login view"""

    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks")

    # once the form is submitted, login the user
    def form_valid(self, form):
        user = form.save()  # save the user
        if user is not None:  # if there is a user
            login(self.request, user)  # feed this to login page
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasks")
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    """Class to list all the tasks and render the view"""

    # looks for template task_list by default
    model = Task
    # by default django looks for template task_list.html, override it by defining the template_name
    context_object_name = "tasks"  # by default we have the context object name as object_list, we will over ride it here!

    # helps us override the data that is passed to the view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()

        # search button logic
        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(title__icontains=search_input)
        context["search_input"] = search_input
        return context


# create
class TaskCreate(LoginRequiredMixin, CreateView):
    """Class to create a task and render the view"""

    # this will search for a template named task_form.html
    model = Task
    fields = [
        "title",
        "description",
        "complete",
    ]  # to list out the elements in the form
    success_url = reverse_lazy("tasks")

    # to set the default user automatically
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


# read
class TaskDetail(LoginRequiredMixin, DetailView):
    """Class to list each task in detail and render the view"""

    # will search for the template base/task.html, since we over rided it
    model = Task
    context_object_name = "task"
    template_name = "base/task.html"


# update
class TaskUpdate(LoginRequiredMixin, UpdateView):
    """Class to update a task and render the view"""

    # uses the same form as in the create view
    model = Task
    fields = [
        "title",
        "description",
        "complete",
    ]  # to list out the elements in the form  # to list out all the elements in the form
    success_url = reverse_lazy("tasks")


# delete
class TaskDelete(LoginRequiredMixin, DeleteView):
    """Class to delete a task and render the view"""

    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")
