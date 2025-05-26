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
        session.duration = timedelta(seconds=elapsed_seconds) 
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

from datetime import timedelta, datetime
from collections import defaultdict
from django.utils import timezone
from django.db.models.functions import TruncDate, TruncDay, TruncHour
from django.db.models import Sum
import json

def format_duration(minutes):
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins else f"{hours}h"
    return f"{minutes}m"

@login_required
def dashboard(request):
    now = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=6)
    month_start = today.replace(day=1)

    # -- DAILY: bugünkü saatlik veriler
    daily_sessions = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date=today
    ).annotate(hour=TruncHour('start_time')) \
     .values('hour') \
     .annotate(total=Sum('duration'))
    # Session sayıları (adet)
    daily_count = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date=today
    ).count()

    weekly_count = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date__gte=week_start
    ).count()

    monthly_count = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date__gte=month_start
    ).count()

    daily_map = {entry['hour'].hour: int(entry['total'].total_seconds() // 60) for entry in daily_sessions}
    daily_labels = [f"{h:02d}:00" for h in range(24)]
    daily_data = [daily_map.get(h, 0) for h in range(24)]

    # -- WEEKLY: son 7 güne göre
    weekly_sessions = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date__gte=week_start
    ).annotate(day=TruncDate('start_time')) \
     .values('day') \
     .annotate(total=Sum('duration'))

    weekly_map = {entry['day']: int(entry['total'].total_seconds() // 60) for entry in weekly_sessions}
    weekly_labels = [(week_start + timedelta(days=i)).strftime('%a') for i in range(7)]
    weekly_data = [weekly_map.get(week_start + timedelta(days=i), 0) for i in range(7)]

    # -- MONTHLY: bu ayın günlerine göre
    days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day
    monthly_sessions = PomodoroSession.objects.filter(
        user=request.user,
        is_completed=True,
        start_time__date__gte=month_start
    ).annotate(day=TruncDay('start_time')) \
     .values('day') \
     .annotate(total=Sum('duration'))

    monthly_map = {entry['day'].day: int(entry['total'].total_seconds() // 60) for entry in monthly_sessions}
    month_name = today.strftime("%b")  # örnek: May
    monthly_labels = [f"{day} {month_name}" for day in range(1, days_in_month + 1)]
    monthly_data = [monthly_map.get(day, 0) for day in range(1, days_in_month + 1)]

    # -- CONTEXT
    context = {
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),

        'weekly_labels': json.dumps(weekly_labels),
        'weekly_data': json.dumps(weekly_data),

        'monthly_labels': json.dumps(monthly_labels),
        'monthly_data': json.dumps(monthly_data),

        'weekly_total_minutes': sum(weekly_data),  
        'daily_total': format_duration(sum(daily_data)),
        'weekly_total': format_duration(sum(weekly_data)),
        'monthly_total': format_duration(sum(monthly_data)),
        'daily_count': daily_count,
        'weekly_count': weekly_count,
        'monthly_count': monthly_count,

    }

    return render(request, 'pomodoro/dashboard.html', context)
