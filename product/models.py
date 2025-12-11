from django.db import models
from django.contrib.auth.models import User
class Category(models.Model):
    name=models.CharField(max_length=100)
    slug=models.SlugField(unique=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to='product/')
    recipe=models.TextField(blank=True)

    
    def __str__(self):
        return self.name


class Order(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    delivery_date = models.DateField()
    message = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}kg for {self.user.username if self.user else 'Guest'}"

    



    
