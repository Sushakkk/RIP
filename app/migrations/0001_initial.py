# Generated by Django 4.2.7 on 2024-10-24 15:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('img_url', models.URLField(blank=True, verbose_name='URL изображения')),
                ('category', models.CharField(max_length=100, verbose_name='Категория')),
                ('status', models.CharField(choices=[('active', 'Действует'), ('deleted', 'Удалена')], default='active', max_length=10, verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'Деятельность',
                'verbose_name_plural': 'Деятельности',
                'db_table': 'activities',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SelfEmployed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(default='Не указано', max_length=100, verbose_name='ФИО')),
                ('inn', models.CharField(blank=True, default='Отсутствует', max_length=12, null=True, verbose_name='ИНН')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('completion_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('status', models.CharField(choices=[('draft', 'Черновик'), ('deleted', 'Удалена'), ('formed', 'Сформирована'), ('completed', 'Завершена'), ('rejected', 'Отклонена')], default='draft', max_length=100, verbose_name='Статус')),
                ('moderator', models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='moderator_user', to=settings.AUTH_USER_MODEL, verbose_name='Модератор')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='self_employed_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Самозанятый',
                'verbose_name_plural': 'Самозанятые',
                'db_table': 'self_employed',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='SelfEmployedActivities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('importance', models.BooleanField(default=False, verbose_name='Главная деятельность')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='self_employed_activities', to='app.activities', verbose_name='Деятельность')),
                ('self_employed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='app.selfemployed', verbose_name='Самозанятый')),
            ],
            options={
                'verbose_name': 'Деятельности Самозанятого',
                'verbose_name_plural': 'Деятельности Самозанятых',
                'db_table': 'self_employed_activities',
                'ordering': ('id',),
            },
        ),
    ]
