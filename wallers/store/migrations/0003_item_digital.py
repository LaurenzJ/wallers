# Generated by Django 3.1.6 on 2021-03-05 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_customer_order_orderitem_shippingaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='digital',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
