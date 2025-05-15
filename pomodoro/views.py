import json
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import localtime
from .models import PomodoroSession
from .utils import get_total_duration, format_duration
import json
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import PomodoroSession
from .utils import get_total_duration, format_duration  # varsa


# ---------------------------

@login_required
def start_pomodoro(request):
    """ Yeni bir Pomodoro oturumu başlatır. """
    if request.method == "POST":
        data = json.loads(request.body)
        duration_minutes = int(data.get("duration", 0))

        if duration_minutes <= 0:
            return JsonResponse({"status": "error", "message": "Geçersiz süre!"})

        # Aktif oturum kontrolü
        active_session = PomodoroSession.objects.filter(user=request.user, is_completed=False).first()
        if active_session:
            elapsed = (now() - active_session.start_time).total_seconds()
            if elapsed >= active_session.duration.total_seconds():
                active_session.is_completed = True
                active_session.end_time = now()
                active_session.save()
            else:
                return JsonResponse({"status": "error", "message": "Zaten aktif bir oturumun var!"})

        # Yeni oturum oluştur
        session = PomodoroSession.objects.create(
            user=request.user,
            start_time=now(),
            duration=timedelta(minutes=duration_minutes),
            is_completed=False
        )

        return JsonResponse({"status": "started", "session_id": session.id})

    # GET isteği için sayfa render
    past_sessions = PomodoroSession.objects.filter(user=request.user, is_completed=True).order_by("-start_time")
    active_session = PomodoroSession.objects.filter(user=request.user, is_completed=False).first()

    return render(request, "pomodoro/start_pomodoro.html", {
        "past_sessions": past_sessions,
        "active_session": active_session
    })


# ---------------------------

@login_required
def get_active_pomodoro(request):
    """ Sayfa yenilendiğinde aktif oturumun süresini döndürür. """
    session = PomodoroSession.objects.filter(user=request.user, is_completed=False).first()

    if session:
        start_time = session.start_time.timestamp()
        duration = session.duration.total_seconds()
        elapsed_time = int(now().timestamp()) - int(start_time)
        remaining_time = max(duration - elapsed_time, 0)

        if remaining_time <= 1:
            session.is_completed = True
            session.end_time = now()
            session.save()
            return JsonResponse({"status": "inactive"})

        return JsonResponse({
            "status": "active",
            "session_id": session.id,
            "remaining_time": int(remaining_time),
            "total_duration": int(session.duration.total_seconds()),
            "start_time": localtime(session.start_time).isoformat()
        })

    return JsonResponse({"status": "inactive"})


# ---------------------------

@login_required
def complete_pomodoro(request, session_id):
    if request.method == "POST":
        session = get_object_or_404(PomodoroSession, id=session_id, user=request.user)

        if session.is_completed:
            return JsonResponse({"status": "error", "message": "Bu oturum zaten tamamlandı!"})

        data = json.loads(request.body)
        elapsed_seconds = data.get("elapsed_time")

        if elapsed_seconds is None:
            return JsonResponse({"status": "error", "message": "Geçen süre alınamadı!"})

        now_time = now()
        session.end_time = now_time
        session.duration = timedelta(seconds=elapsed_seconds)  # 👈 Gerçek geçen süre
        session.is_completed = True
        session.save()

        return JsonResponse({
            "status": "completed",
            "duration": str(session.duration)
        })

    return JsonResponse({"status": "error", "message": "Geçersiz istek!"})

# ---------------------------

@login_required
def pomodoro_history(request):
    sessions = PomodoroSession.objects.filter(user=request.user, is_completed=True).order_by("-start_time")
    return render(request, "pomodoro/pomodoro_history.html", {"sessions": sessions})


# ---------------------------

@login_required
def clear_sessions(request):
    if request.method == 'POST':
        PomodoroSession.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success', 'message': 'Geçmiş oturumlar başarıyla silindi.'})

    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=400)


# ---------------------------

from datetime import timedelta
from collections import defaultdict

@login_required
def dashboard(request):
    now = timezone.now().date()
    week_start = now - timedelta(days=6)

    # Verileri çek
    sessions = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date__gte=week_start
    ).annotate(day=TruncDate('start_time')) \
     .values('day') \
     .annotate(total=Sum('duration')) \
     .order_by('day')

    # Günlük süreleri haritalayalım
    duration_map = {entry['day']: int(entry['total'].total_seconds() // 60) for entry in sessions}

    labels = []
    data = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        labels.append(day.strftime('%a'))  # Mon, Tue, ...
        data.append(duration_map.get(day, 0))

    context = {
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(data),
        'daily_labels': json.dumps(labels),
        'daily_data': json.dumps(data),
        'monthly_labels': json.dumps(labels),
        'monthly_data': json.dumps(data),
        'weekly_total_minutes': sum(data),
        'daily_total': f"{data[-1]} min",
        'weekly_total': f"{sum(data)} min",
        'monthly_total': f"{sum(data)} min",
        'daily_count': len([d for d in data if d > 0]),
        'weekly_count': len([d for d in data if d > 0]),
        'monthly_count': len([d for d in data if d > 0]),
    }

    return render(request, 'pomodoro/dashboard.html', context)
