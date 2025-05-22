from django.urls import path
from .views import weekly_leaderboard_view, monthly_leaderboard_view,leaderboard_page

urlpatterns = [
    path("", leaderboard_page, name="leaderboard"),
    path('weekly/', weekly_leaderboard_view, name='weekly_leaderboard'),
    path('monthly/', monthly_leaderboard_view, name='monthly_leaderboard'),
]
