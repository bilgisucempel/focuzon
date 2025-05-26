from django.urls import path
from . import views
from . import friend_views

urlpatterns = [
    path("start/", views.start_pomodoro, name="start_pomodoro"),
    path("complete/<int:session_id>/", views.complete_pomodoro, name="complete_pomodoro"),
    path("history/", views.pomodoro_history, name="pomodoro_history"),
    path('get_active/', views.get_active_pomodoro, name='get_active_pomodoro'),
    path('clear_sessions/', views.clear_sessions, name='clear_sessions'),
    path('dashboard/', views.dashboard, name='dashboard'),

      # 💜 Arkadaşlık yolları
    

    path('send_request/<int:user_id>/', friend_views.send_friend_request, name='send_request'),
    path('accept_request/<int:request_id>/', friend_views.accept_friend_request, name='accept_request'),
    path('friends/', friend_views.friend_list, name='friend_list'),

    path('users/', friend_views.user_list, name='user_list'),
    path('pending_requests/', friend_views.pending_requests, name='pending_requests'),
    path('friends/add/<int:user_id>/', friend_views.send_friend_request, name='send_friend_request'),
    path('friends/activity/', friend_views.friends_activity, name='friends_activity'),




]
