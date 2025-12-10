from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),                
    path('product/', views.products, name='products'),  
    path('category/<slug:slug>', views.category_products, name='category_products'),

]
