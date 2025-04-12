# Generated by Django 5.1.7 on 2025-04-12 17:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("subastas", "0005_auction_auctioneer"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="auction",
            name="auctioneer",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="auctions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
