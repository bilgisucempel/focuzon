from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class PomodoroSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)  # Geçen süre burada saklanıyor
    is_completed = models.BooleanField(default=False)

    def formatted_duration(self):
        if self.duration:
            total_seconds = int(self.duration.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            return f"{minutes} dakika {seconds} saniye"
        return "Tamamlanmadı"

    def __str__(self):
        return f"{self.user.username} - {self.formatted_duration()}"   # Liste görünümü için şirin bir ek 😍

# -----------------------------
class Friendship(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendship_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendship_requests_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_friendship')
        ]
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'

    def __str__(self):
        status = "✅ Arkadaş" if self.accepted else "⏳ Bekliyor"
        return f"{self.from_user.username} ➡️ {self.to_user.username} | {status}"

