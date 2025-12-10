from django.contrib import admin
from .models import Product,Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('name','price','category')
    search_fields=('name',)
    list_filter=('category',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','slug')
    prepopulated_fields={'slug':('name',)}

