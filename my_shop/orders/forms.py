from django import forms


class CreateOrderForm(forms.Form):

    phone = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    requires_delivery = forms.ChoiceField()
    delivery_city = forms.CharField(required=False)
    delivery_adress = forms.CharField(required=False)
    shop = forms.CharField(required=False)
    payment_on_get = forms.ChoiceField()
