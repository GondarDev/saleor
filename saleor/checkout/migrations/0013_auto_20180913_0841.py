# Generated by Django 2.0.8 on 2018-09-13 13:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("checkout", "0012_remove_cartline_data")]

    operations = [
        migrations.RenameField(
            model_name="cartline", old_name="data_new", new_name="data"
        ),
        migrations.AlterUniqueTogether(
            name="cartline", unique_together={("cart", "variant", "data")}
        ),
    ]
