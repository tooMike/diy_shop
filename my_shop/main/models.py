from django.contrib.auth import get_user_model
from django.db import models

from main.choices import COLOUR


User = get_user_model()


class Shop(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название магазина")
    adress = models.TextField(max_length=300, verbose_name="Адрес магазина")

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "Магазины"

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название категории")
    description = models.TextField(
        max_length=450, verbose_name="Описание категории")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Colour(models.Model):
    name = models.CharField(max_length=30, choices=COLOUR, verbose_name="Название цвета")

    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "Цвета"

    def __str__(self) -> str:
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название страны")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "страна"
        verbose_name_plural = "Страны"


class Manufacturer(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Название производителя")
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name="Страна производителя"
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "производитель"
        verbose_name_plural = "Производители"


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название товара")
    description = models.TextField(
        max_length=400, verbose_name="Описание товара")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена")
    sale = models.IntegerField(null=True, blank=True, verbose_name="Скидка")
    rating = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Рейтинг", default=0
    )
    category = models.ForeignKey(
        Category, verbose_name="Категрия", on_delete=models.CASCADE
    )
    manufacturer = models.ForeignKey(
        Manufacturer, verbose_name="Производитель", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
        default_related_name = "product"

    def __str__(self) -> str:
        return self.name


class ProductItem(models.Model):
    serial_number = models.IntegerField(
        null=True, blank=True, verbose_name="Серийный номер"
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE)
    shop = models.ForeignKey(
        Shop, verbose_name="Магазин", on_delete=models.CASCADE)
    colour = models.ManyToManyField(Colour, verbose_name="цвет")

    class Meta:
        verbose_name = "единица товара"
        verbose_name_plural = "Единицы товаров"
