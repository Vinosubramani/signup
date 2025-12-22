from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   
    path('products/', views.products, name='products'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<int:pk>/order/', views.product_order, name='product_order'),
    path('product/<int:pk>/recipe/', views.product_recipe, name='product_recipe'),
    path("payu/start/<int:order_id>/", views.payu_payment, name="payu_start"),
    
    # path("payu/success/<int:order_id>/", views.payu_success, name="payu_success"),
    # path("payu/failure/<int:order_id>/", views.payu_failure, name="payu_failure"),


]
