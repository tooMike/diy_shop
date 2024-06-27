from django.db import models
from django.contrib.auth import get_user_model
from main.models import Product


User = get_user_model()


class CartQueryset(models.QuerySet):
    """Переопределяем QuerySet для ShoppingCart."""

    def total_price(self):
        """Метод для расчета общей стоимости корзины."""
        return sum(cart.product_price() for cart in self)

    def total_quantity(self):
        """Метод для расчета суммарного количества товаров в корзине."""
        if self:
            return sum(cart.quantity for cart in self)
        return 0


class ShoppingCart(models.Model):
    """Модель корзины товаров."""

    # Делаем поле user необязательным, чтобы корзиной могли пользоваться
    # неаторизованные пользователи
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        Product, verbose_name="Товар", on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField(verbose_name="Количество")
    # Добавляем поле чтобы session_key для неаторизованных пользователей
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата добавления"
    )

    objects = CartQueryset().as_manager()

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "Корзины"
        default_related_name = "shoppingcart"

    def __str__(self) -> str:
        return f"Корзина {self.user.username} | Товар {self.product} | Количество {self.quantity}"

    def product_price(self):
        """Метод для возврата стоимости одной позиции в корзине."""
        return round(self.product.actual_price * self.quantity, 2)
