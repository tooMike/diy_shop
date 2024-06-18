from django.db import models

from users.constants import CONFIRMATION_CODE_MAX_LENGTH


class EmailCode(models.Model):
    email = models.EmailField(max_length=254)
    code = models.TextField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH, blank=True
    )
