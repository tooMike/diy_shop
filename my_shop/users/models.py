from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class MyUser(AbstractUser):
    adress = models.TextField(max_length=300, blank=True, null=True, verbose_name="Адрес")
    phone = models.CharField(max_length=10, blank=True, null=True, verbose_name="Телефон")

    def get_absolute_url(self):
        return reverse("users:profile")
