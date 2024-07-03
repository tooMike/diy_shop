from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from users.validators import validate_phone_number


class MyUser(AbstractUser):
    city = models.TextField(
        max_length=30, blank=True, null=True, verbose_name="Город"
    )
    adress = models.TextField(
        max_length=300, blank=True, null=True, verbose_name="Адрес"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Телефон",
        validators=(validate_phone_number,),
    )

    def get_absolute_url(self):
        return reverse("users:profile")
