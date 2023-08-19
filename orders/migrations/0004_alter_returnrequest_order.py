# Generated by Django 4.2.3 on 2023-08-14 14:11
from __future__ import annotations

import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_remove_coupon_is_used_coupon_redeemed_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="returnrequest",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="return_requests",
                to="orders.order",
            ),
        ),
    ]