from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='product/')
    recipe = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.IntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    
    delivery_date = models.DateField(null=True, blank=True)

    message = models.CharField(max_length=200, blank=True)

    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )

    payment_gateway = models.CharField(max_length=50, default='PayU')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.payment_status}"



class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at