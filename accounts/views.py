from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import CustomUserForm  # sadece bu kaldı

User = get_user_model()

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("home")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import CustomUser

@login_required
def home(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user
        except:
            profile = None
    return render(request, "home.html", {"profile": profile})


@login_required
def profile_view(request):
    user = request.user
    form = CustomUserForm(instance=user)

    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': user,
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})
