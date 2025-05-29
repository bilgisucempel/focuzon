from django import forms
from .models import FocusRoom

class FocusRoomForm(forms.ModelForm):
    class Meta:
        model = FocusRoom
        fields = ['name', 'description']
