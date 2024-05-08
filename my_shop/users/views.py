from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import (CodeVerificationForm, CustomUserCreationForm,
                         CustomUserUpdateForm, EmailVerificationForm)
from users.user_auth_utils import create_confirmation_code
from users.views_mixins import UserNotAuthenticatedMixin

User = get_user_model()


def email_verification(request):
    initial_data = {}
    if request.session.get('user_email'):
        initial_data['email'] = request.session['user_email']

    form = EmailVerificationForm(request.POST or None, initial=initial_data)
    context = {'form': form}

    # Если пользователь указал правильный незанятый емейл
    # то отправляем ему письмо с кодом подтверждения
    if form.is_valid():
        confirmation_code = create_confirmation_code()
        # Получаем email пользователя
        user_email = form.cleaned_data['email']
        send_mail(
            subject='Регистрация на сайте ShoppingOnline',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email='sir.petri-petrov@yandex.ru',
            recipient_list=[user_email],
            fail_silently=True,
        )
        # Сохраняем код в сессии
        request.session['confirmation_code'] = confirmation_code
        request.session['user_email'] = user_email
        # Отправляем пользователя на форму проверки кода подтверждения
        return redirect('users:code_verification')
    return render(request, 'registration/email_verification_form.html', context)


def code_verification(request):
    # Получаем email пользователя из сессии
    initial_data = {
        'email': request.session.get('user_email',)
    }
    form = CodeVerificationForm(request.POST or None, initial=initial_data)
    context = {'form': form}
    if form.is_valid():
        user_code = form.cleaned_data['code']
        # Проверяем совпадает ли введенный пользователем код
        # с кодом, сохраненным в сессии
        if user_code == request.session.get('confirmation_code'):
            request.session['user_email'] = initial_data['email']
            return redirect('users:registration')
        else:
            form.add_error(None, 'Неверный код подтверждения')
    return render(request, 'registration/code_verification_form.html', context)


class UserRegistration(UserNotAuthenticatedMixin, CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')

    # Получаем email из сессии и устанавливаем его
    # как начального значения для поля email формы
    def get_initial(self):
        initial = super(UserRegistration, self).get_initial()
        user_email = self.request.session.get('user_email', None)
        if user_email:
            initial['email'] = user_email
        return initial


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/profile.html'
    form_class = CustomUserUpdateForm

    def get_object(self):
        return self.request.user
