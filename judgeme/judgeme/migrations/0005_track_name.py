# Generated by Django 4.1.2 on 2022-11-02 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgeme', '0004_rename_top_songs_jmuser_top_tracks'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='name',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
