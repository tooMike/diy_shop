from django import forms


class CartAddForm(forms.Form):
    """Форма для добавления товара в корзину."""

    colorproduct_id = forms.IntegerField()
