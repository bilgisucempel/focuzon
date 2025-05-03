from django.urls import path ,include
from .views import register, user_login, user_logout, profile_view

urlpatterns = [
    path("register/", register, name="register"),  # Kayıt ol sayfası
    path("login/", user_login, name="login"),  # Giriş yap sayfası
    path("logout/", user_logout, name="logout"),  # Çıkış yapma işlemi
    path("profile/", profile_view, name="profile"),

]
