from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from shopping_cart.models import ShoppingCart
from users.forms import (CodeVerificationForm, CustomUserCreationForm,
                         CustomUserUpdateForm, EmailVerificationForm)
from users.tasks import send_email_task
from users.user_auth_utils import create_confirmation_code
from users.views_mixins import UserNotAuthenticatedMixin

User = get_user_model()


def email_verification(request):
    """Представление для отправки кода подтверждения на емейл пользователя."""
    initial_data = {}
    if request.session.get("user_email"):
        initial_data["email"] = request.session["user_email"]

    form = EmailVerificationForm(request.POST or None, initial=initial_data)
    context = {"form": form}

    # Если пользователь указал правильный незанятый емейл
    # то отправляем ему письмо с кодом подтверждения
    if form.is_valid():
        confirmation_code = create_confirmation_code()
        # Получаем email пользователя
        user_email = form.cleaned_data["email"]
        send_email_task.delay(
            subject="Регистрация на сайте ShoppingOnline",
            message=f"""
            Подтверждение регистрации для пользователя: {user_email}
            Ваш код подтверждения: {confirmation_code}
            """,
            from_email="sir.petri-petrov@yandex.ru",
            recipient_list=[user_email],
        )
        # Сохраняем код в сессии
        request.session["confirmation_code"] = confirmation_code
        request.session["user_email"] = user_email
        # Отправляем пользователя на форму проверки кода подтверждения
        return redirect("users:code_verification")
    return render(
        request, "registration/email_verification_form.html", context
    )


def code_verification(request):
    """Представление для проверки кода подтверждения."""
    # Получаем email пользователя из сессии
    initial_data = {
        "email": request.session.get(
            "user_email",
        )
    }
    form = CodeVerificationForm(request.POST or None, initial=initial_data)
    context = {"form": form}
    if form.is_valid():
        user_code = form.cleaned_data["code"]
        # Проверяем совпадает ли введенный пользователем код
        # с кодом, сохраненным в сессии
        if user_code == request.session.get("confirmation_code"):
            request.session["user_email"] = initial_data["email"]
            return redirect("users:registration")
        else:
            form.add_error(None, "Неверный код подтверждения")
    return render(request, "registration/code_verification_form.html", context)


class UserRegistration(UserNotAuthenticatedMixin, CreateView):
    template_name = "registration/registration_form.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")

    # Получаем email из сессии и устанавливаем его
    # как начальное значения для поля email формы
    def get_initial(self):
        initial = super(UserRegistration, self).get_initial()
        user_email = self.request.session.get("user_email", None)
        if user_email:
            initial["email"] = user_email
        return initial


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/profile.html"
    form_class = CustomUserUpdateForm

    def get_object(self):
        return self.request.user


class UserLoginView(LoginView):
    """
    Добавляем логику, чтобы при входе в аккаунт корзина пользователя
    не сбрасывалась. Переводим привязку корзины с session_key на user
    """

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()
        if session_key:
            # Проверяем, нет ли в корзине залогиненного пользователя
            # тех же товаров, что были у анонимного
            # если есть, то увеличиваем их количество
            anon_cart_items = ShoppingCart.objects.filter(
                session_key=session_key
            ).select_related("product")
            user_cart_items = ShoppingCart.objects.filter(
                user=user
            ).select_related("product")

            # Обрабатываем данные так, чтобы избежать
            # множества обращений к БД в цикле
            anonim_item_quantities = {
                item.product: [item.quantity, item] for item in anon_cart_items
            }
            user_item_quantities = {
                item.product: [item.quantity, item] for item in user_cart_items
            }

            to_update_quantity = []
            to_update_user = []

            for product, info in anonim_item_quantities.items():
                if product in user_item_quantities:
                    user_item = user_item_quantities[product][1]
                    user_item.quantity += info[0]
                    to_update_quantity.append(user_item)
                else:
                    info[1].user = user
                    to_update_user.append(info[1])

            if to_update_quantity:
                ShoppingCart.objects.bulk_update(
                    to_update_quantity, ["quantity"]
                )
            if to_update_user:
                ShoppingCart.objects.bulk_update(to_update_user, ["user"])

            # Удаляем корзины анонимного пользователя, которые остались
            # после добавления quantity к корзинам
            # залогиненного пользователя
            ShoppingCart.objects.filter(
                session_key=session_key, user=None
            ).delete()

        return super().form_valid(form)
