from decimal import ROUND_UP, Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from main.choices import RATING_CHOICES

User = get_user_model()


class Shop(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название магазина")
    adress = models.TextField(max_length=300, verbose_name="Адрес магазина")

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "Магазины"
        default_related_name = "shop"

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название категории")
    description = models.TextField(
        max_length=450, verbose_name="Описание категории")
    slug = models.SlugField(unique=True, verbose_name='Идентификатор')
    is_active = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        default_related_name = "category"

    def __str__(self) -> str:
        return self.name


class Colour(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название цвета")

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
        default_related_name = "country"


class Manufacturer(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Название производителя")
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name="Страна производителя"
    )
    slug = models.SlugField(unique=True, verbose_name='Идентификатор')
    is_active = models.BooleanField(default=True, verbose_name='Опубликовано')

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "производитель"
        verbose_name_plural = "Производители"
        default_related_name = "manufacturer"


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название товара")
    description = models.TextField(
        max_length=400, verbose_name="Описание товара")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена")
    sale = models.IntegerField(null=True, blank=True, verbose_name="Скидка")
    actual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена со скидкой",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField(default=True, verbose_name='Опубликовано')
    image = models.ImageField(
        'Изображение',
        upload_to='product_images',
        blank=True
    )
    category = models.ForeignKey(
        Category, verbose_name="Категрия", on_delete=models.CASCADE
    )
    manufacturer = models.ForeignKey(
        Manufacturer, verbose_name="Производитель", on_delete=models.CASCADE
    )
    shop = models.ManyToManyField(
        Shop,
        through='ShopProduct',
        verbose_name='Магазин',
        blank=True
    )
    colour = models.ManyToManyField(
        Colour,
        verbose_name='Цвета товара',
        through='ColourProduct',
    )

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    # @property
    # def price_with_sale(self):
    #     """Расчет новой цены товара с учетом скидки"""
    #     if self.sale:
    #         discount_decimal = Decimal(self.sale) / Decimal(100)
    #         discounted_price = self.price * (Decimal(1) - discount_decimal)
    #         return discounted_price.quantize(Decimal('.01'), rounding=ROUND_UP)
    #     return self.price
    
    def get_absolute_url(self):
        return reverse("main:product_detail", kwargs={"product_id": self.pk})
    
    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "Товары"
        default_related_name = "product"

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if self.sale:
            discount_decimal = Decimal(self.sale) / Decimal(100)
            self.actual_price = self.price * (Decimal(1) - discount_decimal)
            self.actual_price = self.actual_price.quantize(
                Decimal('.01'),
                rounding=ROUND_UP
            )
        else:
            self.actual_price = self.price
        super().save(*args, **kwargs)

    

class SerialNumber(models.Model):
    serial_number = models.CharField(max_length=50, verbose_name="Серийный номер")
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "серийный номер"
        verbose_name_plural = "Серийные номера"


class Review(models.Model):
    text = models.TextField(max_length=1000, verbose_name="Текст отзыва")
    photo = models.FileField("Фото", blank=True, upload_to='photo')
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг",
        choices=RATING_CHOICES
    )
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "Отзывы"
        default_related_name = "reviews"
        ordering = ("-created_at",)


class ShopProduct(models.Model):
    shop = models.ForeignKey(Shop, verbose_name="Магазин", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)


class ColourProduct(models.Model):
    colour = models.ForeignKey(Colour, verbose_name="Цвета", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "цвет товара"
        verbose_name_plural = "Цвета товара"

    def __str__(self):
        return self.colour.name

class ShopProductColourProduct(models.Model):
    shopproduct = models.ForeignKey(ShopProduct, verbose_name="Товар в магазине", on_delete=models.CASCADE)
    colourproduct = models.ForeignKey(ColourProduct, verbose_name="Цвета товара", on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество")
