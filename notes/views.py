from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse



@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user)
    note_id = request.GET.get('note_id')
    selected_note = get_object_or_404(Note, id=note_id, user=request.user) if note_id else notes.first()
    return render(request, 'notes/note_list.html', {'notes': notes, 'selected_note': selected_note})

@login_required
def create_note(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        note = Note.objects.create(user=request.user, title=title, content=content)
        return redirect('notes:note_list')
    return render(request, 'notes/create_note.html')

@login_required
def update_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.title = request.POST.get('title')
        note.content = request.POST.get('content')
        note.save()
        return JsonResponse({"status": "saved"})


def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        return redirect('notes:note_list')  # düzeltildi
    return redirect('notes:note_list')