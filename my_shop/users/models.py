from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class MyUser(AbstractUser):
    adress = models.TextField(max_length=300)

    def get_absolute_url(self):
        return reverse("users:profile")

