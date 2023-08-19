from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import Cart
from .models import CartItem
from .models import Wishlist
from .models import WishlistItem
from offers.models import Offer
from orders.models import Coupon
from users.models import Address
from users.models import Product
from users.models import ProductVariation

# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


from django.db.models import Sum


def inc_cart_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    size = ProductVariation.objects.get(id=item.variation.id)

    if size.stock >= 1:
        size.stock -= 1
        size.save()
        item.quantity += 1
        item.save()

        # Recalculate total, tax, and grand total
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = sum(
            cart_item.product.price * cart_item.quantity
            for cart_item in cart_items
        )
        tax = (2 * total) / 100
        grant_total = total + tax

        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(
                    cart__cart_id=_cart_id(request)
                )

            cart_count = (
                cart_items.aggregate(Sum("quantity"))["quantity__sum"] or 0
            )

        except CartItem.DoesNotExist:
            cart_count = 0

        return JsonResponse(
            {
                "price": item.product.price,
                "quantity": item.quantity,
                "max_quantity": size.stock,
                "total": total,
                "grant_total": grant_total,
                "tax": tax,
                "cart_count": cart_count,
            }
        )
    else:
        return JsonResponse({"error": "Product out of Stock"})


def dec_cart_item(request, item_id):
    item = CartItem.objects.get(id=item_id)
    size = ProductVariation.objects.get(id=item.variation.id)

    if item.quantity > 1:
        size.stock += 1
        size.save()
        item.quantity -= 1
        item.save()

        # Recalculate total, tax, and grand total
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = sum(
            cart_item.product.price * cart_item.quantity
            for cart_item in cart_items
        )
        tax = (2 * total) / 100
        grant_total = total + tax

        try:
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(
                    cart__cart_id=_cart_id(request)
                )

            cart_count = (
                cart_items.aggregate(Sum("quantity"))["quantity__sum"] or 0
            )

        except CartItem.DoesNotExist:
            cart_count = 0

        return JsonResponse(
            {
                "price": item.product.price,
                "quantity": item.quantity,
                "max_quantity": size.stock,
                "total": total,
                "grant_total": grant_total,
                "tax": tax,
                "cart_count": cart_count,
            }
        )
    else:
        size.stock += 1
        size.save()
        item.delete()

        # Recalculate total, tax, and grand total after deleting the item
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        total = sum(
            cart_item.product.price * cart_item.quantity
            for cart_item in cart_items
        )
        tax = (2 * total) / 100
        grant_total = total + tax

        return JsonResponse(
            {
                "removed": True,
                "total": total,
                "grant_total": grant_total,
                "tax": tax,
            }
        )


def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    variation_id = request.POST.get("variation_id")

    # Check if the selected variation exists and is in stock
    if variation_id:
        variation = get_object_or_404(
            ProductVariation, id=variation_id, product=product, stock__gt=0
        )
    else:
        # No variation selected or the selected variation is out of stock
        return redirect(reverse("cart"))

    # Check if the same variation (size and color) is already in the cart
    cart_item = CartItem.objects.filter(
        cart=cart, product=product, variation=variation
    ).first()

    if cart_item:
        # Variation already in cart, increment the quantity and save
        cart_item.quantity += 1
        cart_item.save()
    else:
        # Variation not in cart, add it to the cart
        if request.user.is_authenticated:
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                user=current_user,
                product=product,
                variation=variation,
                defaults={"quantity": 1},
            )
        else:
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variation=variation,
                defaults={"quantity": 1},
            )

    # Redirect to cart view
    return redirect(reverse("cart"))


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(
                product=product, user=request.user, id=cart_item_id
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(
                product=product, cart=cart, id=cart_item_id
            )
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(
            product=product, user=request.user, id=cart_item_id
        )
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(
            product=product, cart=cart, id=cart_item_id
        )
    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True
            )
        else:
            cart_items = CartItem.objects.filter(
                cart__cart_id=_cart_id(request), is_active=True
            )

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass  # just ignore

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "cart/cart.html", context)


def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user, name="Default Wishlist"
    )
    wishlist_item, item_created = WishlistItem.objects.get_or_create(
        wishlist=wishlist, product=product, cart=cart
    )

    return redirect(
        "product_details",
        category_slug=product.category.slug,
        product_slug=product.slug,
    )


def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, pk=item_id)

    if wishlist_item.wishlist.user == request.user:
        wishlist_item.delete()

    return redirect("wishlist")


@login_required
def wishlist(request):
    try:
        wishlist = Wishlist.objects.filter(user=request.user).latest(
            "created_at"
        )
    except Wishlist.DoesNotExist:
        wishlist = None

    products = Product.objects.all().filter(is_available=True)

    if wishlist:
        wishlist_items = WishlistItem.objects.filter(wishlist=wishlist)
    else:
        wishlist_items = []

    return render(
        request,
        "user/wishlist.html",
        {"wishlist_items": wishlist_items, "products": products},
    )


def checkout(request):
    try:
        tax = 0
        grand_total = 0
        addresses = None
        default_address = None

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(
                user=request.user, is_active=True
            )
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        total = sum(
            cart_item.product.price * cart_item.quantity
            for cart_item in cart_items
        )
        tax = Decimal(2) * total / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass  # just ignore

    try:
        if request.user.is_authenticated:
            addresses = Address.objects.filter(customer=request.user)
            default_address = addresses.get(default=True)
    except Address.DoesNotExist:
        pass

    context = {
        "total": total,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
        "addresses": addresses,
        "default_address": default_address,
    }
    return render(request, "cart/checkout.html", context)
