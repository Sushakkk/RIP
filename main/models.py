# from django.db import models
# from django.contrib.auth.models import User


# class Orders(models.Model):
#     STATUS_CHOICES = [
#         ('draft', 'Черновик'),
#         ('deleted', 'Удалена'),
#         ('formed', 'Сформирована'),
#         ('completed', 'Завершена'),
#         ('rejected', 'Отклонена'),
#     ]

#     created_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
#     formed_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата формирования")
#     completed_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
#     status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")

#     def __str__(self):
#         return f"Order {self.id} by {self.user.username}"

#     class Meta:
#         db_table = "orders"
#         verbose_name = "Заказ"
#         verbose_name_plural = "Заказы"
#         ordering = ("id",)


# class Categories(models.Model):
#     category = models.CharField(max_length=100, verbose_name="Категория")

#     def __str__(self):
#         return self.category

#     class Meta:
#         db_table = "categories"
#         verbose_name = "Категория"
#         verbose_name_plural = "Категории"
#         ordering = ["category"]


# class Services(models.Model):
#     title = models.CharField(max_length=100, verbose_name="Название")
#     description = models.CharField(max_length=250, verbose_name="Описание")
#     img_url = models.URLField(verbose_name="URL изображения")
#     category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='services', verbose_name="Категория")
#     status = models.BooleanField(default=True, verbose_name="Доступность")  # TRUE означает, что услуга доступна

#     def __str__(self):
#         return self.title

#     class Meta:
#         db_table = "services"
#         verbose_name = "Услуга"
#         verbose_name_plural = "Услуги"
#         ordering = ["title"]


# class OrdersServices(models.Model):
#     order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_services', verbose_name="Заказ")
#     service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='order_services', verbose_name="Услуга")
#     importance = models.BooleanField(default=False, verbose_name="Главная услуга")

#     class Meta:
#         unique_together = ('order', 'service')  # Составной уникальный ключ
#         db_table = "orders_services"
#         verbose_name = "услуга_заявка"
#         verbose_name_plural = "услуги_заявки"
#         ordering = ['order']  # Упорядочение по заказу

#     def __str__(self):
#         return f"Order {self.order.id} - Service {self.service.title}"


# class Users(models.Model):
#     fio = models.CharField(max_length=100, verbose_name="ФИО")
#     login = models.CharField(max_length=100, unique=True, verbose_name="Логин")
#     password = models.CharField(max_length=100, verbose_name="Пароль")
#     is_stuff = models.BooleanField(default=True, verbose_name="Сотрудник")

#     class Meta:
#         db_table = 'users'
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         ordering = ['fio']

#     def __str__(self):
#         return self.fio
