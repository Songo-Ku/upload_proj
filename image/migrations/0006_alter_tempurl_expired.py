# Generated by Django 3.2.13 on 2022-05-24 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0005_rename_expires_tempurl_expired'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempurl',
            name='expired',
            field=models.DateTimeField(blank=True, verbose_name='Expires'),
        ),
    ]
