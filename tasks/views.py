from django.shortcuts import render, redirect
from .models import Task
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def task_list(request):
    if request.method == "POST":
        title = request.POST.get("title")
        due_date = request.POST.get("due_date") or None
        Task.objects.create(user=request.user, title=title, due_date=due_date)
        return redirect("task_list")

    tasks = Task.objects.filter(user=request.user).order_by("is_completed", "due_date")
    return render(request, "tasks/task_list.html", {"tasks": tasks})

@login_required
def toggle_task(request, task_id):
    task = Task.objects.get(id=task_id, user=request.user)
    task.is_completed = not task.is_completed
    task.save()
    return redirect("task_list")

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('task_list')