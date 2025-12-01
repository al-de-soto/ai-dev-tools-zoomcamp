from django.shortcuts import render, redirect, get_object_or_404
from .models import TODO


def home(request):
    todos = TODO.objects.all()
    return render(request, 'todos/home.html', {'todos': todos})


def create_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        due_date = request.POST.get('due_date')

        TODO.objects.create(
            title=title,
            description=description,
            due_date=due_date if due_date else None
        )
        return redirect('home')

    return render(request, 'todos/create_todo.html')


def edit_todo(request, pk):
    todo = get_object_or_404(TODO, pk=pk)

    if request.method == 'POST':
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description', '')
        due_date = request.POST.get('due_date')
        todo.due_date = due_date if due_date else None
        todo.save()
        return redirect('home')

    return render(request, 'todos/edit_todo.html', {'todo': todo})


def delete_todo(request, pk):
    todo = get_object_or_404(TODO, pk=pk)

    if request.method == 'POST':
        todo.delete()
        return redirect('home')

    return render(request, 'todos/delete_todo.html', {'todo': todo})


def toggle_resolved(request, pk):
    todo = get_object_or_404(TODO, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    return redirect('home')
