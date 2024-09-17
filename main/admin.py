from django.contrib import admin

from .models import Orders, Categories, Services, OrdersServices

admin.site.register(Orders)
admin.site.register(Categories)
admin.site.register(Services)
admin.site.register(OrdersServices)

