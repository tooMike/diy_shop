from collections import defaultdict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models import Sum
from rest_framework import serializers

from api.models import EmailCode
from main.models import (Category, ColorProduct, ColorProductShop, Country,
                         Manufacturer, Product, Review)
from users.constants import (CONFIRMATION_CODE_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                             USERNAME_MAX_LENGTH)
from users.user_auth_utils import create_confirmation_code

User = get_user_model()


class EmailCodeSerializer(serializers.Serializer):
    """Сериализатор для отправки кода подтверждения на емейл пользователя."""

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

    confirmation_code = serializers.SlugField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH, write_only=True
    )
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        """Проверяем корректность пары email-confirmation_code."""
        email = data.get("email")
        confirmation_code = data.get("confirmation_code")
        email_code = EmailCode.objects.filter(
            email=email, code=confirmation_code
        ).first()
        if email_code:
            return data
        raise serializers.ValidationError(
            "Предоставлены неверный email или код подтверждения"
        )

    def create(self, validated_data):
        # Удаляем confirmation_code из данных
        validated_data.pop("confirmation_code", None)
        # Шифруем пароль
        validated_data["password"] = make_password(
            validated_data.get("password")
        )
        return super(UserRegistrationSerializer, self).create(validated_data)

    class Meta:
        model = User
        fields = ("username", "email", "confirmation_code", "password")


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(
        max_length=USERNAME_MAX_LENGTH,
        validators=(UnicodeUsernameValidator(),),
    )
    password = serializers.CharField(max_length=PASSWORD_MAX_LENGTH)

    def validate(self, data):
        """Проверяем что пользователь с такими данным существует"""
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            return data
        raise ValidationError("Неверное имя пользователя или пароль")


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    is_active = serializers.BooleanField(write_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "description", "slug", "is_active")


class ManufacturerSerializer(serializers.ModelSerializer):
    """Сериализатор для производителей."""

    is_active = serializers.BooleanField(write_only=True)
    country = serializers.SlugRelatedField(
        queryset=Country.objects.all(), slug_field="name"
    )

    class Meta:
        model = Manufacturer
        fields = ("id", "name", "country", "slug", "is_active")


class ProductsListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка товаров."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="name"
    )
    manufacturer = serializers.SlugRelatedField(
        queryset=Manufacturer.objects.all(), slug_field="name"
    )
    num_shop = serializers.IntegerField()
    num_products = serializers.IntegerField()
    rating = serializers.FloatField()

    class Meta:
        model = Product
        fields = (
            "name",
            "price",
            "sale",
            "actual_price",
            "image",
            "category",
            "manufacturer",
            "num_shop",
            "num_products",
            "rating",
        )


class ProductDetailSerializer(ProductsListSerializer):
    """Сериализатор для конкретного товара."""

    manufacturer = ManufacturerSerializer()
    offline_shops_data = serializers.SerializerMethodField()
    internet_shop_data = serializers.SerializerMethodField()

    def get_offline_shops_data(self, obj):
        """
        Получаем данные о наличии товаров и их цвете
        в оффлайн магазинах.
        """
        grouped_data = defaultdict(list)
        for colorproductshop in (
            ColorProductShop.objects.filter(
                colorproduct__product=obj, quantity__gt=0
            )
            .exclude(shop__name__icontains="Склад")
            .select_related("shop", "colorproduct", "colorproduct__color")
        ):
            grouped_data[colorproductshop.colorproduct].append(
                {
                    "shop": colorproductshop.shop.name,
                    "shop_id": colorproductshop.shop.id,
                    "quantity": colorproductshop.quantity,
                }
            )

        offline_shops_data = [
            {
                "color": colorproduct.color.name,
                "color_id": colorproduct.color.id,
                "items": items,
            }
            for colorproduct, items in grouped_data.items()
        ]

        return offline_shops_data

    def get_internet_shop_data(self, obj):
        """
        Получаем данные о наличии товаров и их цвете
        на складе интернет магазина.
        """
        get_data = (
            ColorProduct.objects.filter(
                product=obj,
                colorproductshop__shop__name__icontains="Склад",
                colorproductshop__quantity__gt=0,
            )
            .select_related("color")
            .annotate(total=Sum("colorproductshop__quantity"))
        )
        internet_shop_data = [
            {
                "color": item.color.name,
                "color_id": item.color.id,
                "quantity": item.total,
            }
            for item in get_data
        ]
        return list(internet_shop_data)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "sale",
            "actual_price",
            "image",
            "category",
            "manufacturer",
            "offline_shops_data",
            "internet_shop_data",
            "rating",
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    def validate(self, data):
        """Пользователь может добавить только 1 отзыв к товару."""
        if self.context.get("request").method == "POST":
            product = self.context.get("view").kwargs.get("product_id")
            author = self.context.get("request").user
            if Review.objects.filter(author=author, product=product).exists():
                raise serializers.ValidationError(
                    "Можно написать только 1 отзыв к товару"
                )
        return data

    class Meta:
        model = Review
        fields = ("id", "text", "photo", "created_at", "rating", "author")
