from __future__ import annotations

from django import forms

from .models import Order, Coupon


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "phone",
            "email",
            "address_line_1",
            "address_line_2",
            "country",
            "state",
            "city",
            "pin_code",
            "order_note",
        ]


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'valid_from', 'valid_to', 'active']
