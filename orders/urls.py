from __future__ import annotations

from django.urls import include
from django.urls import path

from . import views

urlpatterns = [
    path("place_order", views.place_order, name="place_order"),
    path(
        "order_complete/<str:order_number>/",
        views.order_complete,
        name="order_complete",
    ),
    path("order_complete", views.order_complete, name="order_complete"),
    path("payments", views.payments, name="payments"),
    path(
        "payment_through_wallet/<str:order_number>/",
        views.payment_through_wallet,
        name="payment_through_wallet",
    ),
    path(
        "cancel_order/<str:order_number>/",
        views.cancel_order,
        name="cancel_order",
    ),
    path("coupon_view", views.coupon_view, name="coupon_view"),
    path("view_wallet", views.view_wallet, name="view_wallet"),
    path("add_wallet", views.add_wallet, name="add_wallet"),
    path("update_wallet", views.update_wallet, name="update_wallet"),
    path("redeem_coupon", views.redeem_coupon, name="redeem_coupon"),
    path(
        "redeem_coupon_payment/<str:order_number>/",
        views.redeem_coupon_payment,
        name="redeem_coupon_payment",
    ),
    path(
        "return/<str:order_id>/",
        views.return_request_view,
        name="return_request_view",
    ),
    path(
        "return_item/<str:order_id>/",
        views.view_return_items,
        name="view_return_items",
    ),
    path(
        "return_status/<str:order_id>/",
        views.update_return_status,
        name="update_return_status",
    ),
    path("view_returns", views.view_returns, name="view_returns"),
    path("view_coupons", views.view_coupons, name="view_coupons"),
    path("add_coupon", views.add_coupon, name="add_coupon"),
    path("paypal/", include("paypal.standard.ipn.urls")),
]
