from django.contrib import admin
from .models import PomodoroSession, Friendship

admin.site.register(Friendship)

@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_time', 'end_time', 'duration', 'is_completed']
    list_filter = ['user', 'is_completed']
    search_fields = ['user__username']
    ordering = ['-start_time']

fields = ('user', 'start_time', 'duration', 'is_completed')
readonly_fields = ('end_time',)
