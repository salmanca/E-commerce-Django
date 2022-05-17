from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Categories)
admin.site.register(models.Products)
admin.site.register(models.OrderItem)
admin.site.register(models.Order)
admin.site.register(models.Address)
admin.site.register(models.CustomUser)
admin.site.register(models.Coupon)
admin.site.register(models.CategoryOffer)
admin.site.register(models.ProductOffer)