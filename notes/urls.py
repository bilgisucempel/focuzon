from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('create/', views.create_note, name='create_note'),
    path('update/<int:note_id>/', views.update_note, name='update_note'),
    # autosave için
]
