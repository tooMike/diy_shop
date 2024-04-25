from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import CustomUserCreationForm, CustomUserUpdateForm
from users.views_mixins import UserNotAuthenticatedMixin


User = get_user_model()

class UserRegistration(UserNotAuthenticatedMixin, CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile.html'
    # fields = ('username', 'first_name', 'last_name', 'email')
    form_class = CustomUserUpdateForm

    def get_object(self):
        return self.request.user

    # def get_object(self, queryset=None):
    #     obj = super().get_object(queryset)
    #     if obj != self.request.user:
    #         raise Http404("Вы не имеете права редактировать этот профиль")
    #     return obj
