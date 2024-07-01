from django import forms


class CartAddForm(forms.Form):

    product_id = forms.IntegerField()
    colorproduct_id = forms.IntegerField()
