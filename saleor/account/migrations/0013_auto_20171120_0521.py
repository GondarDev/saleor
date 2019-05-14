# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-20 11:21
from __future__ import unicode_literals

from django.db import migrations
from phonenumbers.phonenumberutil import NumberParseException
import phonenumber_field.modelfields
import phonenumbers


def convert_phone_number_to_phonenumberfield(apps, schema_editor):
    Address = apps.get_model("account", "Address")
    for address in Address.objects.all():
        if address.phone:
            try:
                phone_number = phonenumbers.parse(
                    address.phone.raw_input, address.country.code
                )
                address.phone = phone_number
                address.save()
            except NumberParseException:
                pass


class Migration(migrations.Migration):

    dependencies = [("account", "0012_auto_20171117_0846")]

    replaces = [("userprofile", "0013_auto_20171120_0521")]

    operations = [
        migrations.AlterField(
            model_name="address",
            name="phone",
            field=phonenumber_field.modelfields.PhoneNumberField(
                blank=True, default="", max_length=128, verbose_name="phone number"
            ),
        ),
        migrations.RunPython(
            convert_phone_number_to_phonenumberfield, migrations.RunPython.noop
        ),
    ]
