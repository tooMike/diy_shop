from typing import Any
from django import forms

from main.models import Shop
from users.validators import validate_phone_number


class CreateOrderForm(forms.Form):
    """Форма размещения заказа."""

    phone = forms.CharField(max_length=15, validators=(validate_phone_number,))
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    requires_delivery = forms.ChoiceField(
        choices=[
            ("true", "Требуется доставка"),
            ("false", "Получение в магазине"),
        ]
    )
    delivery_city = forms.CharField(required=False, max_length=30)
    delivery_adress = forms.CharField(required=False, max_length=300)
    shop = forms.ModelChoiceField(queryset=Shop.objects.all(), required=False)
    payment_on_get = forms.ChoiceField(
        choices=[
            ("true", "Доставка при получении"),
            ("false", "Оплата картой"),
        ]
    )

    def clean(self):
        cleaned_data = super().clean()
        requires_delivery = cleaned_data.get("requires_delivery") == "true"
        delivery_city = cleaned_data.get("delivery_city")
        delivery_address = cleaned_data.get("delivery_adress")
        shop = cleaned_data.get("shop")

        if requires_delivery:
            if not delivery_city:
                self.add_error('delivery_city', 'Укажите город.')
            if not delivery_address:
                self.add_error('delivery_adress', 'Укажите адрес.')
        else:
            if not shop:
                self.add_error('shop', 'Выберите магазин.')

        return cleaned_data
