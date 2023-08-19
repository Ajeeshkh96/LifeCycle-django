from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account
from .models import Address
from .models import Category
from .models import Product
from .models import ProductVariation
from .models import ProductBannerImage
from .models import ProductImage
# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("category_name",)}
    list_display = ("category_name", "slug")

admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "brand",
        "model",
        "price",
        "category",
        "updated_at",
        "is_available",
    )
    prepopulated_fields = {"slug": ("brand", "model")}

admin.site.register(Product, ProductAdmin)



class AccountAdmin(UserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "username",
        "last_login",
        "date_joined",
        "is_active",
    )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    list_display_links = ("email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)

admin.site.register(Account, AccountAdmin)



admin.site.register(ProductImage)
admin.site.register(ProductBannerImage)
admin.site.register(Address)
admin.site.register(ProductVariation)