from decimal import ROUND_UP, Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from main.choices import RATING_CHOICES

User = get_user_model()


class Shop(models.Model):
    """Модель магазина."""

    name = models.CharField(
        max_length=150, verbose_name="Название магазина", unique=True
    )
    address = models.TextField(
        max_length=300, verbose_name="Адрес магазина", unique=True
    )

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "Магазины"
        default_related_name = "shop"
        unique_together = ("name", "address")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """Модель категория товаров."""

    name = models.CharField(
        max_length=50, verbose_name="Название категории", unique=True
    )
    description = models.TextField(
        max_length=450, verbose_name="Описание категории"
    )
    slug = models.SlugField(unique=True, verbose_name="Идентификатор")
    is_active = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        default_related_name = "category"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Color(models.Model):
    """Модель цвета товара."""

    name = models.CharField(
        max_length=30, verbose_name="Название цвета", unique=True
    )

    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "Цвета"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    """Модель страны."""

    name = models.CharField(
        max_length=50, verbose_name="Название страны", unique=True
    )

    class Meta:
        verbose_name = "страна"
        verbose_name_plural = "Страны"
        default_related_name = "country"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Manufacturer(models.Model):
    """Модель производителя."""

    name = models.CharField(
        max_length=50, verbose_name="Название производителя", unique=True
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name="Страна производителя"
    )
    slug = models.SlugField(unique=True, verbose_name="Идентификатор")
    is_active = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "производитель"
        verbose_name_plural = "Производители"
        default_related_name = "manufacturer"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Модель товара."""

    name = models.CharField(
        max_length=50, verbose_name="Название товара", unique=True
    )
    description = models.TextField(
        max_length=400, verbose_name="Описание товара"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена"
    )
    sale = models.IntegerField(null=True, blank=True, verbose_name="Скидка")
    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена со скидкой",
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    is_active = models.BooleanField(default=True, verbose_name="Опубликовано")
    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Время добавления"
    )
    image = models.ImageField(
        "Изображение", upload_to="product_images", blank=True
    )
    category = models.ForeignKey(
        Category, verbose_name="Категрия", on_delete=models.CASCADE
    )
    manufacturer = models.ForeignKey(
        Manufacturer, verbose_name="Производитель", on_delete=models.CASCADE
    )
    color = models.ManyToManyField(
        Color,
        verbose_name="Цвета товара",
        through="ColorProduct",
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
        default_related_name = "product"
        ordering = ("created",)

    def __str__(self) -> str:
        return self.name

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return 0

    def get_absolute_url(self):
        return reverse("main:product_detail", kwargs={"product_id": self.pk})

    def save(self, *args, **kwargs):
        if self.sale:
            discount_decimal = Decimal(self.sale) / Decimal(100)
            self.actual_price = self.price * (Decimal(1) - discount_decimal)
            self.actual_price = self.actual_price.quantize(
                Decimal(".01"), rounding=ROUND_UP
            )
        else:
            self.actual_price = self.price
        super().save(*args, **kwargs)


class ColorProduct(models.Model):
    """Модель для связи товаров и их цветов."""

    color = models.ForeignKey(
        Color, verbose_name="Цвет", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "цвет товара"
        verbose_name_plural = "Цвета товара"
        default_related_name = "colorproduct"
        unique_together = ("color", "product")

    def __str__(self):
        return self.color.name


class ColorProductShop(models.Model):
    """
    Модель для связи товаров определенных цветов
    с их наличиев в магазинах.
    """

    colorproduct = models.ForeignKey(
        ColorProduct, verbose_name="Цвет товара", on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop, verbose_name="Магазин", on_delete=models.CASCADE
    )
    quantity = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "товар в магазине"
        verbose_name_plural = "Товары в магазине"
        default_related_name = "colorproductshop"
        unique_together = ("colorproduct", "shop")


class Review(models.Model):
    """Модель отзыва на товар."""

    text = models.TextField(max_length=1000, verbose_name="Текст отзыва")
    photo = models.FileField("Фото", blank=True, upload_to="photo", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг", choices=RATING_CHOICES
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"
        default_related_name = "reviews"
        ordering = ("-created_at",)
