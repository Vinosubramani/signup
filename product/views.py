from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Product, Category, Order
from .utils import generate_payu_hash
from django.contrib.auth.decorators import login_required


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

        # basic validation
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

        # ✅ PAYMENT STARTS ONLY HERE
        return redirect("start_payment", order.id)

    return render(request, "product/order.html", {"product": product})


# ---------------- PAYU START ----------------
def start_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    txnid = f"TXN{order.id}"

    firstname = request.user.username if request.user.is_authenticated else "Guest"
    email = request.user.email if request.user.is_authenticated else "guest@test.com"

    hash_data = [
        settings.PAYU_KEY,
        txnid,
        str(order.amount),
        order.product.name,
        firstname,
        email,
        '', '', '', '', '', '', '', '', ''
    ]

    hash_value = generate_payu_hash(hash_data, settings.PAYU_SALT)

    return render(request, "product/payu_dummy_form.html", {
        "key": settings.PAYU_KEY,
        "txnid": txnid,
        "amount": order.amount,
        "productinfo": order.product.name,
        "firstname": firstname,
        "email": email,
        "hash": hash_value,
        "order": order
    })


# ---------------- PAYU GATEWAY (DUMMY) ----------------
def payu_gateway(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "product/payu_gateway.html", {"order": order})


# ---------------- PAYMENT RESULT ----------------
def payu_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = "SUCCESS"
    order.save()
    return render(request, "product/success.html", {"order": order})


def payu_failure(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = "FAILED"
    order.save()
    return render(request, "product/failure.html", {"order": order})
