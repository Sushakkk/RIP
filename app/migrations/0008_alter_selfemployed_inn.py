# Generated by Django 4.2.7 on 2024-10-24 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_selfemployed_inn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selfemployed',
            name='INN',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='ИНН'),
        ),
    ]
