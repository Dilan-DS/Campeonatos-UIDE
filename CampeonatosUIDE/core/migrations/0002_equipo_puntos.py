# Generated by Django 5.2.3 on 2025-07-01 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="equipo",
            name="puntos",
            field=models.IntegerField(default=0),
        ),
    ]
