from collections import defaultdict

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.models import EmailCode
from main.models import (Category, Color, ColorProduct, ColorProductShop,
                         Country, Manufacturer, Product, Review, Shop)
from orders.models import Order
from orders.utils import (get_available_products, prepare_order_products,
                          update_user_info)
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
        raise serializers.ValidationError(
            "Неверное имя пользователя или пароль"
        )


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
        max_length=30, min_length=3, required=False
    )
    delivery_adress = serializers.CharField(
        max_length=150, min_length=3, required=False
    )
    shop = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), required=False
    )
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

    def validate(self, data):
        """
        Проверяем, что у пользователя добавлены товары в корзину
        и нужное количество каждого товара есть в выбранном магазине.
        """
        user = data.get("user")
        carts = ShoppingCart.objects.filter(user=user)

        if not carts.exists():
            raise serializers.ValidationError(
                "Нельзя создать заказ с пустой корзиной."
            )

        requires_delivery = data["requires_delivery"]

        if requires_delivery:
            shop = get_object_or_404(Shop, name__icontains="Склад")
        else:
            shop = data["shop"]

        product_quantities = get_available_products(user=user, shop=shop)
        for item in carts:
            product_quantity = product_quantities.get(item.colorproduct_id)
            # Проверяем доступен ли конкретный товар в выбранном магазине
            if not product_quantity:
                raise serializers.ValidationError(
                    f"В выбранном магазине товар {item.product} \
                    {item.colorproduct} отсутствует. Выберите другой магазин."
                )
            if product_quantity.total < item.quantity:
                raise serializers.ValidationError(
                    f"Недостаточное количество товаров: {item.product}: \
                    {item.colorproduct}. В наличии: {product_quantity.total}"
                )
        # Добаляем данные, чтобы не запрашивать их в методах create заново
        data["carts"] = carts
        data["product_quantities"] = product_quantities
        data["shop"] = shop
        return data

    @transaction.atomic
    def create(self, validated_data):
        user = validated_data["user"]
        requires_delivery = validated_data["requires_delivery"]
        payment_on_get = validated_data["payment_on_get"]
        carts = validated_data["carts"]
        product_quantities = validated_data["product_quantities"]
        shop = validated_data["shop"]

        # Сохраняем данные в модель пользователя,
        # если этих данных еще нет
        update_user_info(user=user, cleaned_data=validated_data)

        # Cоздаем заказ
        order_data = {
            "user": user,
            "phone": validated_data["phone"],
            "requires_delivery": requires_delivery,
            "shop": shop,
            "payment_on_get": payment_on_get,
        }
        if requires_delivery:
            order_data["delivery_city"] = validated_data["delivery_city"]
            order_data["delivery_adress"] = validated_data["delivery_adress"]
        order = Order.objects.create(**order_data)

        # Формируем список товаров для этого заказа
        # и список нового наличия в магазинах
        orderproduct, shop_quantity = prepare_order_products(
            carts, product_quantities, order
        )

        # Обновляем наличие в магазинах для всех позиций в заказе
        ColorProductShop.objects.bulk_update(shop_quantity, ["quantity"])

        # Создаем записи в БД для всех позиций в заказе
        OrderProduct.objects.bulk_create(orderproduct)

        # Очищаем корзину пользователя
        carts.delete()

        return super().create(validated_data)
