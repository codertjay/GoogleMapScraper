# Generated by Django 4.1.7 on 2023-04-02 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("map_scrapers", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="history",
            old_name="country",
            new_name="address",
        ),
    ]