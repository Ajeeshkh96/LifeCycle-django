from __future__ import annotations

from django.db.models import Sum

from .models import Cart
from .models import CartItem
from carts.views import _cart_id
from carts.models import WishlistItem


def counter(request):
    cart_count = 0
    wishlist_count = 0

    if "admin" in request.path:
        return {}
    else:
        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
                wishlist_items = WishlistItem.objects.filter(wishlist__user=request.user)
            else:
                cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))
                wishlist_items = WishlistItem.objects.filter(cart__cart_id=_cart_id(request))

            cart_count = cart_items.aggregate(Sum("quantity"))["quantity__sum"] or 0
            wishlist_count = wishlist_items.aggregate(Sum("quantity"))["quantity__sum"] or 0

        except CartItem.DoesNotExist:
            cart_count = 0

    return {"cart_count": cart_count, "wishlist_count": wishlist_count}


