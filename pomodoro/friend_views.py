from django.contrib.auth import get_user_model

User = get_user_model()

from django.db import models
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import PomodoroSession, Friendship



# 🎀 Arkadaşlık İsteği Gönderme
from django.shortcuts import redirect

@login_required
def send_friend_request(request, user_id):
    if request.user.id == user_id:
        return redirect('user_list')  # Kendine istek olmaz

    to_user = get_object_or_404(User, id=user_id)
    friendship, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)

    if not created:
        return redirect('user_list')  # Zaten istek varsa geri dön

    return redirect('user_list')  # Başarılıysa da geri dön


# 🎀 Arkadaşlık İsteği Kabul Etme
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(Friendship, id=request_id, to_user=request.user)

    if friend_request.accepted:
        return redirect('pending_requests')  # Hatalıysa da redirect et

    friend_request.accepted = True
    friend_request.save()
    return redirect('pending_requests')  # Başarılıysa da redirect et


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
def pending_requests(request):
    requests = Friendship.objects.filter(to_user=request.user, accepted=False)
    return render(request, 'pomodoro/pending_requests.html', {'requests': requests})

from django.db.models import Q

@login_required
def user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)

    if query:
        users = users.filter(username__icontains=query)

    # Gönderilen arkadaşlık istekleri
    sent_requests = Friendship.objects.filter(from_user=request.user)
    sent_user_ids = sent_requests.values_list('to_user_id', flat=True)

    # Zaten arkadaş olunanlar
    friendships = Friendship.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
    )

    friend_user_ids = [
        f.to_user.id if f.from_user == request.user else f.from_user.id
        for f in friendships
    ]

    return render(request, 'pomodoro/user_list.html', {
        'users': users,
        'sent_user_ids': sent_user_ids,
        'friend_user_ids': friend_user_ids,
    })



from django.utils.timezone import now, localdate
from django.db.models import Sum

@login_required
def friends_activity(request):
    today = localdate()

    # Arkadaşları bul
    friendships = Friendship.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
    )

    # Arkadaş kullanıcılarını ayır
    friend_users = [
        f.to_user if f.from_user == request.user else f.from_user
        for f in friendships
    ]

    friend_stats = []
    for friend in friend_users:
        # Bugünkü toplam süreyi hesapla
        today_sessions = PomodoroSession.objects.filter(
            user=friend,
            is_completed=True,
            start_time__date=today
        ).aggregate(total=Sum('duration'))

        # Dakikaya çevir
        total_minutes = int(today_sessions['total'].total_seconds() // 60) if today_sessions['total'] else 0

        # Aktif mi kontrol et
        is_active = PomodoroSession.objects.filter(user=friend, is_completed=False).exists()

        friend_stats.append({
            'username': friend.username,
            'total_today': total_minutes,
            'is_active': is_active,
        })

    # HTML'e gönder
    return render(request, 'pomodoro/friends_activity.html', {
        'friend_stats': friend_stats
    })
