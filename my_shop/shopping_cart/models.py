from django.db import models
from django.contrib.auth import get_user_model
from main.models import Product


User = get_user_model()


class ShoppingCart(models.Model):
    """Модель корзины товаров."""

    user = models.ForeignKey(
        User, verbose_name="Пользователь", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "Корзины"
        default_related_name = "shoppingcart"
