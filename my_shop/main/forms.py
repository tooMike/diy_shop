from django import forms

from main.choices import RATING_CHOICES
from main.models import Review


class ReviewForm(forms.ModelForm):

    text = forms.CharField(
        label="Текст отзыва:",
        widget=forms.Textarea(
            attrs={"class": "form-control w-100", "rows": 3, "required": True}
        ),
    )
    rating = forms.ChoiceField(
        label="Поставьте оценку:",
        choices=RATING_CHOICES,
        widget=forms.Select(),
        required=True,
    )
    photo = forms.FileField(label="Добавьте фото:", required=False)

    class Meta:
        model = Review
        fields = ("text", "rating", "photo")


class PriceFilterForm(forms.Form):
    price_min = forms.IntegerField(
        label="Минимальная цена",
        required=False,
        widget=forms.NumberInput(attrs={"min": 0}),
    )
    price_max = forms.IntegerField(label="Максимальная цена", required=False)
