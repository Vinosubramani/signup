from django.contrib import admin
from .models import Product, Category, Order, EmailOTP


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ('user_id','id','user', 'quantity', 'delivery_date', 'message','payment_status', 'created_at')
    can_delete = False

    # Disable the add button in inline
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = [OrderInline]  


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user_id','id','product', 'user', 'quantity', 'delivery_date', 'message','payment_status','created_at',)
    list_filter = ('delivery_date',)
    search_fields = ('product__name', 'user__username', 'message')
    readonly_fields = ('product', 'user', 'quantity', 'delivery_date', 'message', 'created_at')

    
    def has_add_permission(self, request):
        return False

    
    def has_change_permission(self, request, obj=None):
        return False

   
    def has_delete_permission(self, request, obj=None):
        return True

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display=("email","otp","expires_at")
    list_filter=("expires_at",)
    earch_fields=("email",)

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj =None):
        return False
    
    def has_delete_permission(self,reuest, ob=None):
        return True
       