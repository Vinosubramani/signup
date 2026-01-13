# product/urls.py
from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<int:pk>/', views.product_order, name='product_order'),
    path('product/<int:pk>/recipe/', views.product_recipe, name='product_recipe'),
    
    # Payment URLs
    path('order/<int:order_id>/pay/', views.payu_payment, name='payu_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('payment/payu/webhook/',views.payu_webhook,name='payu_webhook'),
    path("my_order/", views.my_order, name="my_order"),
    path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
     path("otp-login/", views.otp_login_page, name="otp_login"),
    
    

]