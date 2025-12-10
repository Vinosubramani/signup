from django.shortcuts import render,get_object_or_404
from .models import Product,Category

def home(request):
    categories=Category.objects.all()
    products=Product.objects.all()
    print('categories',categories )
    print('products',products)
    return render(request, 'product/home.html', {'categories': categories, 'products': products})

def products(request):
    products = Product.objects.all()
    return render(request, 'product/products.html', {'products': products})

def category_products(request,slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'product/category.html', {'category': category, 'products': products})


