# Generated by Django 4.1.1 on 2022-12-02 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('judgeme', '0025_remove_image_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='jmuser',
            name='up_image',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='judgeme.image'),
        ),
    ]