from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_pic_preview')  # ✅ Kullanıcı ve Profil Resmi eklendi

    def profile_pic_preview(self, obj):
        return f'<img src="{obj.profile_pic.url}" width="50px" style="border-radius:50%;">'  # ✅ Küçük profil fotoğrafı
    profile_pic_preview.allow_tags = True
    profile_pic_preview.short_description = 'Profil Resmi'



