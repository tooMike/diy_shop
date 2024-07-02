from django import forms

from main.models import Shop


class CreateOrderForm(forms.Form):
    """Форма размещения заказа."""

    phone = forms.CharField(max_length=10)
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
    shop = forms.ModelChoiceField(
        queryset=Shop.objects.all(), required=False
    )
    payment_on_get = forms.ChoiceField(
        choices=[
            ("true", "Доставка при получении"),
            ("false", "Оплата картой"),
        ]
    )
