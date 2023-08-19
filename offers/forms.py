from __future__ import annotations

from django import forms

from users.models import ProductBannerImage


class ProductBannerImageForm(forms.ModelForm):
    class Meta:
        model = ProductBannerImage
        fields = ["product", "image"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control-file"}),
        }


from .models import Offer


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            "name",
            "description",
            "start_date",
            "end_date",
            "discount_percentage",
            "applicable_products",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "discount_percentage": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "applicable_products": forms.SelectMultiple(
                attrs={"class": "form-control"}
            ),
        }
