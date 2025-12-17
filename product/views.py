import uuid
from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Category, Order
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

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

        amount = product.price * float(quantity)
        txnid = f"MOCK-{uuid.uuid4()}"

        order = Order.objects.create(
            product=product,
            user=request.user,
            quantity=quantity,
            amount=amount,
            delivery_date=delivery_date,
            message=message,
            txnid=txnid,
            payment_status='PENDING'
        )
        return redirect('mock_payment', order.id)

    return render(request, 'product/order.html', {'product': product})

       


