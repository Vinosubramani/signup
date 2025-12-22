from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Product, Category, Order
from .utils import generate_payu_hash
from django.contrib.auth.decorators import login_required
import uuid
from .hash import generate_hash
from django.conf import settings




# ---------------- HOME ----------------
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'product/home.html', {
        'categories': categories,
        'products': products
    })


# ---------------- PRODUCTS ----------------
def products(request):
    products = Product.objects.all()
    return render(request, 'product/products.html', {'products': products})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'product/category.html', {
        'category': category,
        'products': products
    })


def product_recipe(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product/recipe.html', {'product': product})


# ---------------- ORDER DETAILS (DETAILS FIRST) ----------------
def product_order(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        delivery_date = request.POST.get("delivery_date")
        message = request.POST.get("message")

        
        if not quantity or not delivery_date:
            return render(request, "product/order.html", {
                "product": product,
                "error": "All fields are required"
            })

        order = Order.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            quantity=int(quantity),
            delivery_date=delivery_date,
            message=message,
            amount=int(quantity) * product.price,
            payment_status="PENDING"
        )

        return redirect ("product:payu_payment",order_id=order.id)
    return render(request,"product/order.html",{"product":product})

       
def payu_payment(request, order_id):
    txnid = "txn" + str(uuid.uuid4())[:8]
    
    

    hashh = generate_hash(
        settings.PAYU_KEY,
        settings.PAYU_SALT,
        txnid,
        "500",
        "iPhone",
        "PayU User",
        "test@gmail.com"
    )

    context = {
        "key": settings.PAYU_KEY,
        "txnid": txnid,
        "amount": "500",
        "productinfo": "iPhone",
        "firstname": "PayU User",
        "email": "test@gmail.com",
        "hash": hashh,
    }

    return render(request, "product/payu.html", context)
