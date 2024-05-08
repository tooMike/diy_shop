from django import forms
from django.contrib.auth.forms import UserCreationForm

from main.models import User
from users.validators import email_validator
from users.constants import CONFIRMATION_CODE_MAX_LENGTH


class EmailVerificationForm(forms.Form):
    """Форма для ввода и подтверждения емейла"""
    email = forms.EmailField(required=True, validators=(email_validator,))


class CodeVerificationForm(forms.Form):
    """Форма для ввода и проверка кода подтверждения"""
    email = forms.EmailField(label='Ваш емейл', disabled=True)
    code = forms.CharField(max_length=CONFIRMATION_CODE_MAX_LENGTH, label='Код подтверждения')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label='E-mail', disabled=True)

    class Meta:
        model = User
        fields = ('username', 'email')


class CustomUserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='Адрес электронной почты', disabled=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        help_texts = {
            'username': 'Username изменить нельзя',
        }
