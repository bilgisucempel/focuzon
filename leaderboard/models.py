from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WeeklyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start = models.DateField()  # Pazartesi günü
    total_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'week_start')
        ordering = ['-total_minutes']

    def __str__(self):
        return f"{self.user.username} - {self.total_minutes} dk - Hafta: {self.week_start}"


class MonthlyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()  # Ayın ilk günü
    total_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'month')
        ordering = ['-total_minutes']

    def __str__(self):
        return f"{self.user.username} - {self.total_minutes} dk - Ay: {self.month}"
