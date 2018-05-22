# Generated by Django 2.0.3 on 2018-05-22 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_auto_20180426_0641'),
        ('shipping', '0008_auto_20180108_0814'),
        ('cart', '0006_auto_20180221_0825'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='billing_address',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.Address'),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_address',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='account.Address'),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carts', to='shipping.ShippingMethodCountry'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.RemoveField(
            model_name='cart',
            name='checkout_data',
        ),
        migrations.AddField(
            model_name='cart',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
    ]
