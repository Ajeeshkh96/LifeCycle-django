from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("cart", views.cart, name="cart"),
    path("add_cart/<int:product_id>/", views.add_cart, name="add_cart"),
    path(
        "remove_cart/<int:product_id>/<int:cart_item_id>/",
        views.remove_cart,
        name="remove_cart",
    ),
    path(
        "remove_cart_item/<int:product_id>/<int:cart_item_id>/",
        views.remove_cart_item,
        name="remove_cart_item",
    ),
    path(
        "inc_cart_item/<item_id>/", views.inc_cart_item, name="inc_cart_item"
    ),
    path(
        "dec_cart_item/<item_id>/", views.dec_cart_item, name="dec_cart_item"
    ),
    path(
        "add-to-wishlist/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist",
    ),
    path(
        "remove-from-wishlist/<int:item_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path("wishlist", views.wishlist, name="wishlist"),
    path("checkout", views.checkout, name="checkout"),
    # path('update_cart/', views.update_cart, name='update_cart'),
]
