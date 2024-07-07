from django.contrib.auth import get_user_model
from django.db import models

from main.models import ColorProduct, Product, Shop

User = get_user_model()


class OrderProductQuerySet(models.QuerySet):

    def total_price(self):
        return sum(cart.products_price() for cart in self)

    def total_quantity(self):
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class Order(models.Model):
    """Модель заказа."""

    user = models.ForeignKey(
        to=User,
        verbose_name="Пользователь",
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания заказа"
    )
    phone = models.CharField(verbose_name="Номер телефона", max_length=20)
    requires_delivery = models.BooleanField(
        verbose_name="Требуется доставка", default=False
    )
    delivery_city = models.CharField(
        max_length=30, verbose_name="Город доставки", null=True, blank=True
    )
    delivery_adress = models.CharField(
        max_length=150, verbose_name="Адрес доставки", null=True, blank=True
    )
    shop = models.ForeignKey(
        to=Shop,
        verbose_name="Забор из магазина",
        on_delete=models.SET_DEFAULT,
        default=None,
        blank=True,
        null=True,
    )
    payment_on_get = models.BooleanField(
        verbose_name="Оплата при получении", default=False
    )
    is_paid = models.BooleanField(verbose_name="Заказ оплачен", default=False)
    status = models.CharField(
        verbose_name="Статус заказа", max_length=50, default="В обработке"
    )

    class Meta:
        verbose_name = "заказ"
        verbose_name_plural = "Заказы"
        default_related_name = "orders"

    def __str__(self) -> str:
        return f"Заказ № {self.id} | Покупатель: {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        to=Order, verbose_name="Заказ", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        to=Product,
        verbose_name="Товар",
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
    )
    colorproduct = models.ForeignKey(
        to=ColorProduct,
        verbose_name="Цвет товара",
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=7, decimal_places=2, verbose_name="Цена продажи"
    )
    quantity = models.PositiveIntegerField(
        default=0, verbose_name="Количество"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата продажи"
    )

    objects = OrderProductQuerySet.as_manager()

    class Meta:
        verbose_name: str = "заказанный товар"
        verbose_name_plural = "Заказанные товары"
        default_related_name = "orderedproducts"

    def __str__(self) -> str:
        return f"Товар № {self.product.name} | Заказ: {self.order.id}"

    def total_price(self):
        return round(self.product.actual_price * self.quantity, 2)
