from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser

User = get_user_model()

# Kullanıcı Kaydı Formu
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

# Profil Güncelleme Formu
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_pic"]
