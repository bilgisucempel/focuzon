from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser


# Kullanıcı Kaydı Formu
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()  # DÜZELTİLDİ ✅
        fields = ["username", "email", "password1", "password2"]


# Profil düzenleme için form
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_pic']
