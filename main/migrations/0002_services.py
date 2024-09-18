# Generated by Django 4.2.7 on 2024-09-18 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Services',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.CharField(max_length=250, verbose_name='Описание')),
                ('img_url', models.URLField(verbose_name='URL изображения')),
                ('status', models.BooleanField(default=True, verbose_name='Доступность')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='main.categories', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Услуга',
                'verbose_name_plural': 'Услуги',
                'db_table': 'services',
                'ordering': ['title'],
            },
        ),
    ]
