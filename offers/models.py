from __future__ import annotations

from django.db import models

from users.models import Product

# Create your models here.


class Offer(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    applicable_products = models.ManyToManyField(Product)
