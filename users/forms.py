from __future__ import annotations

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from .models import Account
from .models import Address
from .models import Product
from .models import ProductVariation


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter Password",
                "class": "form-control",
            }
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "password",
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password does not match!")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs[
            "placeholder"
        ] = "Enter First Name"
        self.fields["last_name"].widget.attrs[
            "placeholder"
        ] = "Enter last Name"
        self.fields["phone_number"].widget.attrs[
            "placeholder"
        ] = "Enter Phone Number"
        self.fields["email"].widget.attrs[
            "placeholder"
        ] = "Enter Email Address"
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "brand",
            "model",
            "category",
            "price",
            "description",
            "frame_material",
            "wheel_size",
            "gears",
            "is_available",
        ]

    def __str__(self):
        return self.as_table()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].widget.attrs["placeholder"] = "Enter brand"
        self.fields["model"].widget.attrs["placeholder"] = "Enter model"
        self.fields["price"].widget.attrs["placeholder"] = "Enter price"
        self.fields["description"].widget.attrs[
            "placeholder"
        ] = "Enter product description"
        self.fields["frame_material"].widget.attrs[
            "placeholder"
        ] = "Enter frame material"
        self.fields["wheel_size"].widget.attrs[
            "placeholder"
        ] = "Enter wheel size"
        self.fields["gears"].widget.attrs["placeholder"] = "Enter gears"


class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "brand",
            "model",
            "category",
            "price",
            "description",
            "frame_material",
            "wheel_size",
            "gears",
            "is_available",
        ]


class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['frame_size', 'color', 'stock']


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address_line",
            "address_line2",
            "town_city",
            "country",
            "state",
            "postcode",
            "delivery_instructions",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "First Name",
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "Last Name",
            }
        )

        self.fields["phone"].widget.attrs.update(
            {"class": "form-control mb-2 account-form", "placeholder": "Phone"}
        )

        self.fields["email"].widget.attrs.update(
            {"class": "form-control mb-2 account-form", "placeholder": "email"}
        )

        self.fields["address_line"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "address line",
            }
        )
        self.fields["address_line2"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "address line2",
            }
        )
        self.fields["town_city"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "town city",
            }
        )
        self.fields["country"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "country",
            }
        )
        self.fields["state"].widget.attrs.update(
            {"class": "form-control mb-2 account-form", "placeholder": "state"}
        )
        self.fields["postcode"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "postcode",
            }
        )

        self.fields["delivery_instructions"].widget.attrs.update(
            {
                "class": "form-control mb-2 account-form",
                "placeholder": "delivery instructions",
            }
        )
