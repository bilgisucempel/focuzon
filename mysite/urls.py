from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', home, name='home'),
    path("pomodoro/", include("pomodoro.urls")),
    path('leaderboard/', include('leaderboard.urls')),
    path('tasks/', include('tasks.urls')),
    path('notes/', include('notes.urls', namespace='notes')),
    path('focus/', include('focus.urls')),  # ✅ Çakışmadan kurtarıldı
]

# Medya dosyalarını göstermek için:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
