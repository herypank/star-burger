# Generated by Django 3.0.7 on 2021-01-25 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0036_auto_20210125_1647'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MyModel',
            new_name='Order',
        ),
    ]
