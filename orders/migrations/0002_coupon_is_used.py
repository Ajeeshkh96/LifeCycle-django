# Generated by Django 4.2.3 on 2023-08-14 11:45
from __future__ import annotations

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="coupon",
            name="is_used",
            field=models.BooleanField(default=False),
        ),
    ]
