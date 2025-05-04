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

@login_required
def dashboard(request):
    current_time = timezone.now()

    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = current_time - timedelta(days=7)
    month_ago = current_time - timedelta(days=30)

    daily_sessions = PomodoroSession.objects.filter(user=request.user, start_time__gte=today_start, is_completed=True)
    weekly_sessions = PomodoroSession.objects.filter(user=request.user, start_time__gte=week_ago, is_completed=True)
    monthly_sessions = PomodoroSession.objects.filter(user=request.user, start_time__gte=month_ago, is_completed=True)

    daily_total = get_total_duration(daily_sessions)
    weekly_total = get_total_duration(weekly_sessions)
    monthly_total = get_total_duration(monthly_sessions)

    context = {
        'daily_total': format_duration(daily_total),
        'weekly_total': format_duration(weekly_total),
        'monthly_total': format_duration(monthly_total),
        'daily_count': daily_sessions.count(),
        'weekly_count': weekly_sessions.count(),
        'monthly_count': monthly_sessions.count(),
    }

    last_7_days = PomodoroSession.objects.filter(
        user=request.user,
        start_time__gte=current_time - timedelta(days=7),
        is_completed=True
    ).annotate(day=TruncDate('start_time')).values('day').annotate(total_duration=Sum('duration')).order_by('day')

    labels = []
    data = []

    for entry in last_7_days:
        labels.append(entry['day'].strftime('%d %b'))
        minutes = int(entry['total_duration'].total_seconds() // 60)
        data.append(minutes)

    context.update({
        'chart_labels': labels,
        'chart_data': data
    })

    return render(request, 'pomodoro/dashboard.html', context)
