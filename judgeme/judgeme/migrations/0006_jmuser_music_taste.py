# Generated by Django 4.1.1 on 2022-11-04 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgeme', '0005_track_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmuser',
            name='music_taste',
            field=models.FloatField(default=0, verbose_name=''),
            preserve_default=False,
        ),
    ]
