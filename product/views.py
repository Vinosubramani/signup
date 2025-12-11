from django.shortcuts import render,get_object_or_404
from .models import Product,Category, Order
from django.contrib.auth.decorators import login_required
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

def product_recipe(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product/recipe.html', {'product': product})



@login_required
def product_order(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        kg = request.POST.get('kg')
        delivery_date = request.POST.get('delivery_date')
        message = request.POST.get('message')

        order = Order.objects.create(
            product=product,
            user=request.user,
            quantity=kg,
            delivery_date=delivery_date,
            message=message
        )

        return render(request, 'product/order_success.html', {'order': order})

    return render(request, 'product/order.html', {'product': product})


