from django.contrib import admin
from .models import Product, Category, Order

# ---------- Category Admin ----------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# ---------- Order Inline for Product ----------
class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ('user', 'quantity', 'delivery_date', 'message', 'created_at')
    can_delete = False

    # Disable the add button in inline
    def has_add_permission(self, request, obj=None):
        return False

# ---------- Product Admin ----------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    inlines = [OrderInline]  # Shows related orders inline

# ---------- Order Admin ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity', 'delivery_date', 'message', 'created_at')
    list_filter = ('delivery_date',)
    search_fields = ('product__name', 'user__username', 'message')
    readonly_fields = ('product', 'user', 'quantity', 'delivery_date', 'message', 'created_at')

    # Disable adding new orders manually
    def has_add_permission(self, request):
        return False

    # Disable editing existing orders
    def has_change_permission(self, request, obj=None):
        return False

    # Optional: Disable deleting orders
    def has_delete_permission(self, request, obj=None):
        return False
