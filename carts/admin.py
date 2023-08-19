from django.contrib import admin
from .models import Cart, CartItem, Wishlist,WishlistItem

# Register your models here.

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(WishlistItem)
admin.site.register(Wishlist)
