from django import forms
from datetime import timedelta

# Süre seçenekleri (5'er dakika aralıklarla 3 saate kadar)
POMODORO_DURATIONS = [(i, f"{i} dakika") for i in range(5, 181, 5)]

class PomodoroStartForm(forms.Form):
    duration = forms.ChoiceField(
        label="Çalışma Süresi",
        choices=POMODORO_DURATIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
