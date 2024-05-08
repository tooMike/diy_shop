from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def email_validator(value):
    if User.objects.filter(email=value).first():
        raise ValidationError('Пользователь с таким e-mail уже зарегистрирован')
