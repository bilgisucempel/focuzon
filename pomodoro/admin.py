from django.contrib import admin
from .models import PomodoroSession
from .models import Friendship

admin.site.register(PomodoroSession)
admin.site.register(Friendship)