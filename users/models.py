from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class MyAccountManager(BaseUserManager):
    def create_user(
        self,
        first_name,
        last_name,
        username,
        phone_number,
        email,
        password=None,
    ):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        first_name,
        last_name,
        email,
        username,
        password,
        phone_number=None,
    ):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.phone_number = None
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class BaseModel(models.Model):
    uid = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    # category_image = models.ImageField(upload_to="catgories")

    def get_url(self):
        return reverse("product_by_category", args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.category_name)


class Product(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    rprice = models.IntegerField()
    price = models.IntegerField()
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    description = models.TextField()
    frame_material = models.CharField(max_length=50)
    wheel_size = models.DecimalField(max_digits=4, decimal_places=2)
    gears = models.IntegerField()
    image = models.ImageField(upload_to="photos/products/")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.brand + " " + self.model)

        if self.rprice and self.price:
            self.discount_percentage = (
                (self.rprice - self.price) / self.rprice
            ) * 100

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.model}"

    def get_url(self):
        return reverse("product_details", args=[self.category.slug, self.slug])


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    frame_size = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.frame_size} {self.color} - Stock: {self.stock}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="photos/products/")

    def __str__(self):
        if self.product:
            return f"Product: {self.product.brand}, {self.product.model}"
        else:
            return "Product: N/A"


class ProductBannerImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="photos/product_banners/")
    # Additional fields related to the image or product banner

    def __str__(self):
        return self.image.name


class Address(models.Model):
    """
    Address
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Account, verbose_name=_("Customer"), on_delete=models.CASCADE
    )
    first_name = models.CharField(_("first Name"), max_length=150)
    last_name = models.CharField(_("last Name"), max_length=150)
    phone = models.CharField(_("Phone Number"), max_length=50)
    postcode = models.CharField(_("Postcode"), max_length=50)
    email = models.EmailField(max_length=50)
    address_line = models.CharField(_("Address Line 1"), max_length=255)
    address_line2 = models.CharField(
        _("Address Line 2"), max_length=255, blank=True
    )
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    town_city = models.CharField(_("Town/City/State"), max_length=150)
    delivery_instructions = models.CharField(
        _("Delivery Instructions"), max_length=255
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)
    default = models.BooleanField(_("Default"), default=False)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return "Address"
