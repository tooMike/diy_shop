from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from rest_framework import serializers

from api.models import EmailCode
from main.models import Category, Manufacturer, Product
from users.constants import (CONFIRMATION_CODE_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                             USERNAME_MAX_LENGTH)
from users.user_auth_utils import create_confirmation_code

User = get_user_model()

class EmailCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        confirmation_code = create_confirmation_code()
        email_code, created = EmailCode.objects.get_or_create(**validated_data)
        email_code.code = confirmation_code
        email_code.save()

        send_mail(
            subject="Регистрация на сайте ShoppingOnline",
            message=f"Ваш код подтверждения: {confirmation_code}",
            from_email="sir.petri-petrov@yandex.ru",
            recipient_list=[email_code.email],
            fail_silently=True,
        )
        return email_code
    

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для проверка кода подтверждения емейла."""
    confirmation_code = serializers.SlugField(max_length=CONFIRMATION_CODE_MAX_LENGTH, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        email = data.get("email")
        confirmation_code = data.get("confirmation_code")
        email_code = EmailCode.objects.filter(email=email, code=confirmation_code).first()
        if email_code:
            return data
        raise serializers.ValidationError('Предоставлены неверный email или код подтверждения')

    def create(self, validated_data):
        # Удаляем confirmation_code из данных
        validated_data.pop('confirmation_code', None)
        # Шифруем пароль
        validated_data['password'] = make_password(validated_data.get('password'))
        return super(UserRegistrationSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ('username', 'email', 'confirmation_code', 'password')


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(UnicodeUsernameValidator(),)
    )
    password = serializers.CharField(max_length=PASSWORD_MAX_LENGTH)

    # Проверяем пользователь с такими данным существует
    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            return data
        raise ValidationError("Неверное имя пользователя или пароль")



class ProductSerializer(serializers.ModelSerializer):
    price_with_sale = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name',
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.all(),
        slug_field='name',
    )

    class Meta:
        model = Product
        fields = ('name', 'category', 'manufacturer', 'rating', 'price', 'sale', 'price_with_sale')

    def price_with_sale(self, obj):
        return obj.price_with_sale

