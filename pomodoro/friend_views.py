from django.contrib.auth import get_user_model

User = get_user_model()

from django.db import models
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Friendship

# 🎀 Arkadaşlık İsteği Gönderme
@login_required
def send_friend_request(request, user_id):
    if request.user.id == user_id:
        return JsonResponse({'status': 'error', 'message': 'Kendine arkadaşlık isteği gönderemezsin!'})

    to_user = get_object_or_404(User, id=user_id)
    friendship, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)

    if not created:
        return JsonResponse({'status': 'error', 'message': 'Zaten istekte bulundun!'})

    return JsonResponse({'status': 'success', 'message': 'Arkadaşlık isteği gönderildi!'})

# 🎀 Arkadaşlık İsteği Kabul Etme
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user)

    if friend_request.accepted:
        return JsonResponse({'status': 'error', 'message': 'Zaten kabul edilmiş!'})

    friend_request.accepted = True
    friend_request.save()
    return JsonResponse({'status': 'success', 'message': 'Arkadaşlık isteği kabul edildi!'})

# 🎀 Arkadaş Listesi Görüntüleme
@login_required
def friend_list(request):
    friendships = Friendship.objects.filter(
        (models.Q(from_user=request.user) | models.Q(to_user=request.user)) &
        models.Q(accepted=True)
    )

    friends = []
    for fs in friendships:
        if fs.from_user == request.user:
            friends.append(fs.to_user)
        else:
            friends.append(fs.from_user)

    return render(request, 'pomodoro/friend_list.html', {'friends': friends})

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)  # Kendini listeleme
    return render(request, 'pomodoro/user_list.html', {'users': users})

@login_required
def pending_requests(request):
    requests = Friendship.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'pomodoro/pending_requests.html', {'requests': requests})
