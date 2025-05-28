from django.urls import path
from . import views

app_name = "focus"

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('join/<int:room_id>/', views.join_room, name='join_room'),
    path('', views.room_list, name='focus_home')

]
