from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import FocusRoom, RoomParticipant
from .forms import FocusRoomForm

@login_required
def room_list(request):
    rooms = FocusRoom.objects.all()
    return render(request, 'focus/room_list.html', {'rooms': rooms})

from django.utils import timezone

@login_required
def create_room(request):
    if request.method == 'POST':
        form = FocusRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            return redirect('focus:focus_home')
    else:
        form = FocusRoomForm()
    return render(request, 'focus/create_room.html', {'form': form})

def join_room(request, room_id):
    room = get_object_or_404(FocusRoom, id=room_id)
    participant, created = RoomParticipant.objects.get_or_create(user=request.user, room=room)

    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "start":
            participant.started_at = timezone.now()
            participant.is_active = True
        elif action == "stop":
            participant.is_active = False
        participant.save()

    # tüm aktif katılımcılar
    participants = RoomParticipant.objects.filter(room=room, is_active=True)

    # kullanıcı kendi kaydı
    user_participant = RoomParticipant.objects.filter(user=request.user, room=room).first()

    return render(request, 'focus/room_detail.html', {
        'room': room,
        'participants': participants,
        'user_participant': user_participant,
    })

