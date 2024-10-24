from django.contrib.auth.models import User
from django.db import models
import random

class SelfEmployed(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('deleted', 'Удалена'),
        ('formed', 'Сформирована'),
        ('completed', 'Завершена'),
        ('rejected', 'Отклонена'),
    ]
    fio = models.CharField(max_length=100, verbose_name="ФИО", default='Не указано')
    inn = models.CharField(max_length=12, null=True, blank=True, verbose_name="ИНН", default='Отсутствует')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    modification_date = models.DateTimeField(auto_now=True,blank=True, verbose_name="Дата изменения")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    
    
    # Связь с пользователем (самозанятым)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="self_employed_user", verbose_name="Пользователь")

    # Ограничение выбора модераторов только для пользователей с флагом is_staff=True
    moderator = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        limit_choices_to={'is_staff': True}, 
        related_name="moderator_user", 
        verbose_name="Модератор"
    )

    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    
    def save(self, *args, **kwargs):
        # Если FIO не указано, присваиваем его как комбинацию first_name и last_name пользователя
        if not self.fio or self.fio == 'Не указано':
            self.fio = f"{self.user.last_name} {self.user.first_name}".strip()
        if self.status == 'completed' and self.inn=='Отсутствует':
            self.inn = f"{random.randint(100000000000, 999999999999)}"
        
        super(SelfEmployed, self).save(*args, **kwargs)

    

    def __str__(self):
        return f"Самозанятый {self.id} - {self.user.username}"

    class Meta:
        db_table = "self_employed"
        verbose_name = "Самозанятый"
        verbose_name_plural = "Самозанятые"
        ordering = ("id",)



class Activities(models.Model):
    
    
    STATUS_CHOICES = [
        ('active', 'Действует'),
        ('deleted', 'Удалена'),
    ]
     
    title = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    img_url = models.URLField(blank=True,verbose_name="URL изображения")
    category = models.CharField(max_length=100, verbose_name="Категория")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")

    def __str__(self):
        return self.title

    class Meta:
        db_table = "activities"
        verbose_name = "Деятельность"
        verbose_name_plural = "Деятельности"
        ordering = ("id",)

class SelfEmployedActivities(models.Model):
    self_employed = models.ForeignKey(SelfEmployed, on_delete=models.CASCADE, related_name='activities', verbose_name="Самозанятый")
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, related_name='self_employed_activities', verbose_name="Деятельность")
    importance = models.BooleanField(default=False, verbose_name="Главная деятельность")

    class Meta:
        db_table = "self_employed_activities"
        verbose_name = "Деятельности Самозанятого"
        verbose_name_plural = "Деятельности Самозанятых"
        ordering = ("id",)
        
    def __str__(self):
        return f"{self.self_employed} - {self.activity.title} (Главная: {self.importance})"


