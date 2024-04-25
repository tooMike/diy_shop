from django import forms
from django.contrib.auth.forms import UserCreationForm

from main.models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username',)


class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
        help_texts = {
            'username': 'Username изменить нельзя',
        }
