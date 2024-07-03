import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


def email_validator(value):
    User = get_user_model()
    if User.objects.filter(email=value).first():
        raise ValidationError(
            "Пользователь с таким e-mail уже зарегистрирован"
        )


def validate_phone_number(value):
    phone_regex = re.compile(r"^\+?\d{1,14}[\s\(\)-]*$")
    if not phone_regex.match(value):
        raise ValidationError(
            "Номер телефона должен быть в формате: +XXXXXXXXXXX, \
            где X - цифра. Допускаются пробелы, скобки, знак + и дефисы."
        )
