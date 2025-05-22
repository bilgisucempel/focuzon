from datetime import timedelta, date

from django.contrib.auth import get_user_model
from django.db.models import (
    Sum, Case, When, IntegerField,
    F, ExpressionWrapper
)
from django.shortcuts import render
from django.utils import timezone

from pomodoro.models import PomodoroSession

User = get_user_model()

# ───────────────────────── helpers ──────────────────────────
def get_week_start():
    today = timezone.now().date()
    return today - timedelta(days=today.weekday())          # Monday

def get_month_start():
    today = timezone.now().date()
    return date(today.year, today.month, 1)                 # first of month

# convert PomodoroSession.duration (µs) → minutes
minute_expr = ExpressionWrapper(
    F("pomodorosession__duration") / 60000000,              # 60 s × 1 000 000 µs
    output_field=IntegerField()
)

# ───────────────────── weekly leaderboard ───────────────────
def weekly_leaderboard_view(request):
    week_start = get_week_start()

    global_leaderboard = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=week_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    # if “friends” relation exists, include them; else only self
    if hasattr(request.user, "friends"):
        friends_qs = request.user.friends.all()
        friends_and_self = friends_qs | User.objects.filter(id=request.user.id)
    else:
        friends_and_self = User.objects.filter(id=request.user.id)

    friends_leaderboard = (
        friends_and_self.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=week_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    return render(
        request,
        "leaderboard/weekly.html",
        {
            "global_leaderboard": global_leaderboard,
            "friends_leaderboard": friends_leaderboard,
        },
    )


# ───────────────────── monthly leaderboard ──────────────────
def monthly_leaderboard_view(request):
    month_start = get_month_start()

    global_leaderboard = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=month_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    if hasattr(request.user, "friends"):
        friends_qs = request.user.friends.all()
    else:
        friends_qs = User.objects.none()

    friends_and_self = friends_qs | User.objects.filter(id=request.user.id)

    friends_leaderboard = (
        friends_and_self.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=month_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    return render(
        request,
        "leaderboard/monthly.html",
        {
            "global_leaderboard": global_leaderboard,
            "friends_leaderboard": friends_leaderboard,
        },
    )

# ───────────────────── combined leaderboard page ──────────────────
# views.py  (leaderboard app)

def leaderboard_page(request):
    week_start  = get_week_start()
    month_start = get_month_start()

    # ───── Weekly ──────────────────────────────────────────
    weekly_global = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=week_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    # friends: ya Many-to-Many alanın varsa, yoksa sadece kendin
    if hasattr(request.user, "friends"):
        wf_qs = request.user.friends.all()
    else:
        wf_qs = User.objects.filter(id=request.user.id)

    weekly_friends = (
        (wf_qs | User.objects.filter(id=request.user.id))
        .annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=week_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    # ───── Monthly ─────────────────────────────────────────
    monthly_global = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=month_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    if hasattr(request.user, "friends"):
        mf_qs = request.user.friends.all()
    else:
        mf_qs = User.objects.filter(id=request.user.id)

    monthly_friends = (
        (mf_qs | User.objects.filter(id=request.user.id))
        .annotate(
            total_minutes=Sum(
                Case(
                    When(
                        pomodorosession__start_time__date__gte=month_start,
                        then=minute_expr
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    # tümünü şablona gönder
    return render(
        request,
        "leaderboard/leaderboard.html",
        {
            "weekly_friends":  weekly_friends,
            "weekly_global":   weekly_global,
            "monthly_friends": monthly_friends,
            "monthly_global":  monthly_global,
        },
    )


