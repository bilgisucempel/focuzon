from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import string
import random

class CustomUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True, blank=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        length = 10
        characters = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(characters, k=length))
            if not CustomUser.objects.filter(code=code).exists():
                return code
