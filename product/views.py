from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Product, Category, Order
from django.contrib.auth.decorators import login_required
import uuid
from .hash import generate_hash
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import logging,hashlib
from django.http import HttpResponse
from django.http import JsonResponse
from .models import EmailOTP
from .utils import generate_otp, get_expiry
from .services import send_otp_email
from django.http import JsonResponse
from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)


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

@login_required(login_url='login')
def product_order(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        delivery_date = request.POST.get("delivery_date")
        message = request.POST.get("message")
        
        logger.info(
        "Order details | user=%s | product=%s | quantity=%s | delivery_date=%s | message=%s",
        request.user.username,
        product.name,
        quantity,
        delivery_date,
        message
)

        if not quantity or not delivery_date:
            return render(request, "product/order.html", {
                "product": product,
                "error": "All fields are required"
            })

        order = Order.objects.create(
            product=product,
            user=request.user, 
            quantity=int(quantity),
            delivery_date=delivery_date,
            message=message,
            amount=int(quantity) * product.price,
            payment_status="PENDING"
        )

        return redirect("product:payu_payment", order_id=order.id)
    
    return render(request, "product/order.html", {
        "product": product
    })

@login_required(login_url='login')
def payu_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if order.payment_status == "SUCCESS":
        return redirect("product:my_order")

    order.transaction_id = "TXN" + uuid.uuid4().hex[:12].upper()
    order.payment_status = "PENDING"
    order.save()

    txnid = order.transaction_id
    
    
    amount = str(order.amount)  
    product_name = order.product.name
    user_name = (
        request.user
    )
    user_email = request.user.email 
    
    logger.info(
    "Order created | "
    "order_id=%s | txnid=%s | product=%s | amount=%s | "
    "user_id=%s | username=%s | email=%s",
    order.id,
    txnid,
    product_name,
    amount,
    request.user.id,
    request.user.username,
    user_email
)
    
    hashh = generate_hash(
        settings.PAYU_KEY,
        settings.PAYU_SALT,
        txnid,
        amount,
        product_name,
        user_name,
        user_email,
    )
    logger.info("hashh",hashh)
    
    
    order.transaction_id = txnid
    order.save()

    context = {
        "payu_url": "https://test.payu.in/_payment",
        "key": settings.PAYU_KEY,
        "txnid": txnid,
        "amount": amount,
        "productinfo": product_name,
        "firstname": user_name,
        "email": user_email,
        "phone": request.user.profile.phone if hasattr(request.user, 'profile') and request.user.profile.phone else "9999999999",
        "hash": hashh,
        "surl": request.build_absolute_uri(reverse('product:payment_success')),
        "furl": request.build_absolute_uri(reverse('product:payment_failure')),
        "order": order,
    }

    return render(request, "product/payu.html", context)


# @csrf_exempt
# def payment_success(request):
#     logger.info("Payment callback received")

#     if request.method == 'POST':
#         txnid = request.POST.get('txnid')
#         status = request.POST.get('status')
#         amount = request.POST.get('amount')
#     else:
#         txnid = request.GET.get('txnid')
#         status = request.GET.get('status')
#         amount = request.GET.get('amount')

#     if not txnid:
#         return redirect('product:home')

#     try:
#         order = Order.objects.get(transaction_id=txnid)

        
#         payu_status = (status or "").upper()

#         if payu_status in ["SUCCESS", "COMPLETED"]:
#             order.payment_status = "SUCCESS"
#         else:
#             order.payment_status = "FAILED"

#         order.save()
#         logger.info(f"Payment SUCCESS saved for order_id={order.id}, txnid={txnid}")

#         return render(request, 'product/order_success.html', {
#             'order': order,
#             'transaction_id': txnid,
#             'amount': amount,
#             'status': status
#         })

#     except Order.DoesNotExist:
#         logger.error(f"Order not found for txnid={txnid}")
#         return redirect('product:home')


# @csrf_exempt
# def payment_failure(request):
    
#     if request.method == 'POST':
#         txnid = request.POST.get('txnid')
#         error_message = request.POST.get('error', 'Payment failed')
#     else:
#         txnid = request.GET.get('txnid')
#         error_message = request.GET.get('error', 'Payment failed')
    
#     order = None
#     if txnid:
#         try:
#             order = Order.objects.get(transaction_id=txnid)
#             order.payment_status = "FAILED"
#             order.payment_error = error_message
#             order.save()

#             logger.warning(f"Payment FAILED for order_id={order.id}, txnid={txnid}")
#         except Order.DoesNotExist:
#             pass
        
    
#     return render(request, 'product/failure.html', {
#         'order': order,
#         'error': error_message
#     })



#webhook
@csrf_exempt
def payu_webhook(request):
    
    
    if request.method =="POST":
        logger.info("post reached")
    

        txnid=request.POST.get("txnid")
        status=request.POST.get("status")
        amount = request.POST.get("amount") or request.GET.get("amount")
        received_hash=request.POST.get("hash")

        if not all([txnid, status, amount, received_hash]):
            logger.warning("Missing webhook fields")
            return HttpResponse("Missing fields", status=400)
        
        status = status.strip().lower()
        amount = "{:.2f}".format(float(amount.strip()))

        # txnid="TXNED09E3DF-690"
        # status="success"
        # amount="700"
        # received_hash="e8e5e0da4bf9f77cd51dcd187ba760d32cfef782c8fd9f4533d315ab4827b86da3c38693262a81fc7076b3b9702d868f261705e2464fd1c5e5383e27aa28f50a"

        SALT=settings.PAYU_SALT
        KEY=settings.PAYU_KEY
        hash_string = f"{SALT}|{status}|||||||||{amount}|{txnid}|{KEY}"
        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()
        logger.info("hash:%s",calculated_hash)
        logger.info("hash_string=[%s]", hash_string)
        logger.info("calculated_hash=[%s]", calculated_hash)
        logger.info("received_hash=[%s]", received_hash)

        
        

        if calculated_hash!=received_hash:
            logger.warning("Hash verified mismatch")
            return HttpResponse("Invalid hash", status=400)
        order=Order.objects.filter(transaction_id=txnid)

        if status.lower()=="success":
             order.payment_status="SUCCESS"
        else:
             order.payment_status="FAILED"

        order.save()
        logger.info(f"order updated through webhook|order_id={order.id}")
        return HttpResponse("Ok", status=200)

    return HttpResponse("Invalid request",status=400)

@csrf_exempt
def payment_success(request):
    txnid=request.POST.get("txnid") or request.GET.get("txnid")
    order=Order.objects.filter(transaction_id=txnid).first()
    if order:
        order.payment_status="SUCCESS"
        order.save()
    return render(request,"product/order_success.html",{"order":order})

@csrf_exempt
def payment_failure(request):
    txnid=request.POST.get("txnid") or request.GET.get("txnid")
    order=Order.objects.filter(transaction_id=txnid).first()


    return render(request, "product/failure.html",{"order":order})




def my_order(request):
    
    orders=Order.objects.filter(user=request.user)
    return render(request,"product/my_order.html",{"orders":orders})


@require_POST
def send_otp(request):
    email = request.POST.get("email")

    if not email:
        return JsonResponse(
            {"error": "Email is required"},
            status=400
        )

    otp = generate_otp()
    expiry = get_expiry()

    
    EmailOTP.objects.update_or_create(
        email=email,
        defaults={
            "otp": otp,
            "expires_at": expiry
        }
    )

    try:
        send_otp_email(email, otp)
    except Exception as e:
        return JsonResponse(
            {"error": "Failed to send OTP"},
            status=500
        )

    return JsonResponse({"message": "OTP sent successfully"})





def verify_otp(request):
    email = request.POST.get("email")
    user_otp = request.POST.get("otp")

    try:
        record = EmailOTP.objects.filter(email=email).latest("id")
    except EmailOTP.DoesNotExist:
        return JsonResponse({"error": "OTP not found"}, status=400)

    if record.is_expired():
        return JsonResponse({"error": "OTP expired"}, status=400)

    if record.otp != user_otp:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    record.delete()  

    return JsonResponse({"message": "Login successful"})




def otp_login_page(request):
    return render(request, "product/otp_login.html")

