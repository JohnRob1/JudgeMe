# Generated by Django 4.1.1 on 2022-12-01 02:44

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgeme', '0017_alter_jmuser_music_taste'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jmuser',
            name='music_taste',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), default=list, size=5),
        ),
    ]
