from collections import defaultdict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.models import EmailCode
from main.models import (Category, Color, ColorProduct, ColorProductShop,
                         Country, Manufacturer, Product, Review, Shop)
from orders.models import Order
from shopping_cart.models import ShoppingCart
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

    class Meta:
        model = User
        fields = ("username", "email", "confirmation_code", "password")

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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ("id", "text", "photo", "created_at", "rating", "author")

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


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления нового товара в корзину."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = ("id", "colorproduct", "quantity", "user")
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Добавляем поле product при создании."""
        colorproduct = validated_data.get("colorproduct")
        quantity = validated_data.get("quantity")
        user = validated_data.get("user")
        product = colorproduct.product

        cart = ShoppingCart.objects.create(
            colorproduct=colorproduct,
            quantity=quantity,
            user=user,
            product=product,
        )
        return cart


class ShoppingCartUpdateSerializer(serializers.ModelSerializer):

    quantity = serializers.IntegerField(max_value=32767, min_value=1)

    class Meta:
        model = ShoppingCart
        fields = ("id", "quantity")
        read_only_fields = ("id",)


class ShoppingCartListSerializer(serializers.ModelSerializer):

    color = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    actual_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = (
            "id",
            "product",
            "product_name",
            "colorproduct",
            "color",
            "actual_price",
            "quantity",
        )

    def get_color(self, obj):
        """Получаем цвет товара."""
        return obj.colorproduct.color.name

    def get_product_name(self, obj):
        """Получаем название товара."""
        return obj.product.name

    def get_actual_price(self, obj):
        """Получаем цену товара."""
        return obj.product.actual_price


class OrderCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заказа."""

    delivery_city = serializers.CharField(
        max_lenght=30, min_length=3, required=False
    )
    delivery_adress = serializers.CharField(
        max_lenght=150, min_length=3, required=False
    )
    shop = serializers.PrimaryKeyRelatedField(required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone",
            "requires_delivery",
            "delivery_city",
            "delivery_adress",
            "shop",
            "payment_on_get",
            "is_paid",
            "status",
            "user",
        )
        read_only_fields = ("id", "is_paid", "status")

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data["user"]

        # Сохраняем данные в модель пользователя,
        # если этих данных еще нет
        if not user.first_name:
            user.first_name = validated_data["first_name"]
        if not user.last_name:
            user.last_name = validated_data["last_name"]
        if not user.phone:
            user.phone = validated_data["phone"]
        user.save()

        # Получаем данные о корзинах пользователя
        carts = ShoppingCart.objects.filter(user=user)

        if carts.exists():
            requires_delivery = validated_data["requires_delivery"]
            payment_on_get = validated_data["payment_on_get"]
            if requires_delivery:
                # Ведем проверку по наличию товара на складе интернет магазина
                shop = get_object_or_404(Shop, name__icontains="Склад")
                order = Order.objects.create(
                    user=user,
                    phone=form.cleaned_data["phone"],
                    requires_delivery=requires_delivery,
                    delivery_city=form.cleaned_data["delivery_city"],
                    delivery_adress=form.cleaned_data[
                        "delivery_adress"
                    ],
                    shop=shop,
                    payment_on_get=payment_on_get,
                )
            else:
                shop = form.cleaned_data["shop"]
                order = Order.objects.create(
                    user=user,
                    phone=form.cleaned_data["phone"],
                    requires_delivery=requires_delivery,
                    shop=shop,
                    payment_on_get=payment_on_get,
                )

            # Проверяем, есть ли товары из корзины пользователя
            # в наличии в выбранном магазине
            product_quantities = get_available_products(
                user=user, shop=shop
            )
            if not product_quantities:
                raise ValidationError(
                    "В выбранном магазине товары отсутствуют. \
                    Выберите другой магазин."
                )

            # Формируем записи OrderProduct
            orderproduct = []
            shop_quantity = []
            for item in carts:
                product_quantity = product_quantities.get(
                    item.colorproduct.id, None
                )
                # Проверяем доступен ли конкретный товар
                # в выбранном магазине
                if product_quantity is None:
                    raise ValidationError(
                        f"В выбранном магазине товар {item.product} \
                        отсутствует. Выберите другой магазин."
                    )
                if product_quantity.total < item.quantity:
                    raise ValidationError(
                        f"Недостаточное количество товаров: \
                            {item.product}: {item.colorproduct}. \
                            В наличии: {product_quantity.total}"
                    )
                orderproduct.append(
                    OrderProduct(
                        order=order,
                        product=item.product,
                        colorproduct=item.colorproduct,
                        price=item.product.actual_price,
                        quantity=item.quantity,
                    )
                )

                # Обновляем наличие товара в выбранном магазину
                product_quantity.quantity -= item.quantity
                # Формируем список для bulk_update
                shop_quantity.append(product_quantity)

            # Обновляем наличие в магазинах для всех позиций в заказе
            ColorProductShop.objects.bulk_update(
                shop_quantity, ["quantity"]
            )

            # Создаем записи в БД для всех позиций в заказе
            OrderProduct.objects.bulk_create(orderproduct)

            # Очищаем корзину пользователя
            carts.delete()

            messages.success(request, "Заказ оформлен")
            return redirect("main:index")
        return super().create(validated_data)
