from datetime import timedelta, date
from django.contrib.auth import get_user_model
from django.db.models import (
    Sum, Case, When, IntegerField, F, ExpressionWrapper
)
from django.shortcuts import render
from django.utils import timezone

from pomodoro.models import PomodoroSession, Friendship

User = get_user_model()

# ─────────────── Helpers ────────────────
def get_week_start():
    today = timezone.now().date()
    return today - timedelta(days=today.weekday())

def get_month_start():
    today = timezone.now().date()
    return date(today.year, today.month, 1)

minute_expr = ExpressionWrapper(
    F("pomodorosession__duration") / 60000000,
    output_field=IntegerField()
)

def get_friends_and_self(user):
    friend_ids = Friendship.objects.filter(
        from_user=user, accepted=True
    ).values_list("to_user_id", flat=True)
    return User.objects.filter(id__in=list(friend_ids) + [user.id])

# ─────────────── Weekly ────────────────
def weekly_leaderboard_view(request):
    week_start = get_week_start()

    global_leaderboard = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=week_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    friends_leaderboard = (
        get_friends_and_self(request.user)
        .annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=week_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    return render(request, "leaderboard/weekly.html", {
        "global_leaderboard": global_leaderboard,
        "friends_leaderboard": friends_leaderboard,
    })

# ─────────────── Monthly ────────────────
def monthly_leaderboard_view(request):
    month_start = get_month_start()

    global_leaderboard = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=month_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    friends_leaderboard = (
        get_friends_and_self(request.user)
        .annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=month_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    return render(request, "leaderboard/monthly.html", {
        "global_leaderboard": global_leaderboard,
        "friends_leaderboard": friends_leaderboard,
    })

# ─────────────── Combined Page ────────────────
def leaderboard_page(request):
    week_start = get_week_start()
    month_start = get_month_start()

    global_weekly = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=week_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    global_monthly = (
        User.objects.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=month_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    friends_and_self = get_friends_and_self(request.user)

    friends_weekly = (
        friends_and_self.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=week_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    friends_monthly = (
        friends_and_self.annotate(
            total_minutes=Sum(
                Case(
                    When(pomodorosession__start_time__date__gte=month_start, then=minute_expr),
                    default=0,
                    output_field=IntegerField()
                )
            )
        ).order_by("-total_minutes")
    )

    return render(request, "leaderboard/leaderboard.html", {
        "weekly_global": global_weekly,
        "monthly_global": global_monthly,
        "weekly_friends": friends_weekly,
        "monthly_friends": friends_monthly,
    })
