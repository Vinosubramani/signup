from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import Product, Category, Order, Wishlist
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
from decimal import Decimal
try:
    from .services import send_otp_email
except ImportError:
    def send_otp_email(email, otp):
        pass
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from .utils import apply_product_search



logger = logging.getLogger(__name__)


# ---------------- HOME ----------------
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    featured_products = Product.objects.all()[:3] 
    # request.session['theme'] = 'dark'
    print(request.session.get('theme')) 


    
    # Get user's wishlist if authenticated
    user_wishlist = []
    is_first_order = False
    if request.user.is_authenticated:
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        is_first_order = is_user_first_order(request.user)

    context={ 
            'categories': categories,
            'products': products,
            'featured_products': featured_products,
            'user_wishlist': user_wishlist,
            'is_first_order': is_first_order,
            'theme':request.session.get('theme','dark')
        }
    
    return render(request, 'product/home.html', context)

# ---------------- PRODUCTS ----------------
def products(request):
    products = Product.objects.all()
    return render(request, 'product/products.html', {'products': products})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    
    # Handle search within category
    search_query = request.GET.get('search', '')
    products = apply_product_search(products, search_query)
    
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    is_first_order = False
    if request.user.is_authenticated:
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        is_first_order = is_user_first_order(request.user)

        context={
            'category': category,
            'products': products,
            'search_query': search_query,
            'user_wishlist': user_wishlist,
            'is_first_order': is_first_order
        }
    
    return render(request, 'product/category.html',context) 

def search_products(request):
    search_query = request.GET.get('search', '')
    products = Product.objects.all()
    
    products = apply_product_search(products, search_query)
    
    # Get user's wishlist if authenticated
    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'product/search_results.html', {
        'products': products,
        'search_query': search_query,
        'user_wishlist': user_wishlist
    })

def product_recipe(request, pk):
    product = get_object_or_404(Product, pk=pk)
    other_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:6]
    return render(request, 'product/recipe.html', {
        'product': product,
        'category_slug': product.category.slug,
        'other_products': other_products
    })

@login_required(login_url='login')
def product_order(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        quantity = request.POST.get("quantity")
        delivery_date = request.POST.get("delivery_date")
        message = request.POST.get("message")
        delivery_address = request.POST.get("delivery_address")
        delivery_pincode = request.POST.get("delivery_pincode")
        
        logger.info(
        "Order details | user=%s | product=%s | quantity=%s | delivery_date=%s | message=%s",
        request.user.username,
        product.name,
        quantity,
        delivery_date,
        message
)

        context ={
            "product": product,
            "is_first_order": is_user_first_order(request.user)

        }
        if not all([quantity, delivery_date, delivery_address, delivery_pincode]):
            context["error"] ="All fields are required" 
            return render(request, "product/order.html",context)



        # Validate delivery location
        if not validate_delivery_location(delivery_address, delivery_pincode):
            context["error"]= "Sorry, we only deliver to pincode 635109."
            return render(request, "product/order.html", context)
                
               
            

        # Calculate original amount
        original_amount = int(quantity) * product.price
        
        # Apply first order discount
        discount_info = apply_first_order_discount(request.user, original_amount)
        
        order = Order.objects.create(
            product=product,
            user=request.user, 
            quantity=int(quantity),
            delivery_date=delivery_date,
            message=message,
            delivery_address=delivery_address,
            delivery_pincode=delivery_pincode,
            original_amount=discount_info['original_amount'],
            amount=discount_info['final_amount'],
            is_first_order=discount_info['is_first_order'],
            first_order_discount=discount_info['discount_amount'],
            payment_status="PENDING"
        )

        return redirect("product:payu_payment", order_id=order.id)
    
    # Check if user is eligible for first order discount
    is_first_order = is_user_first_order(request.user)
    
    return render(request, "product/order.html", {
        "product": product,
        "is_first_order": is_first_order
    })

@never_cache
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
    logger.info("hashh: %s",hashh)
    
    
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
    """
    PayU webhook to update order payment status.
    """

    # Handle only POST requests
    if request.method == "POST":
        logger.info("PayU webhook POST received")
        print("Webhook received:", request.POST)

        txnid = request.POST.get("txnid")
        status = request.POST.get("status")
        amount = request.POST.get("amount")
        received_hash = request.POST.get("hash")

        # Check required fields
        if not all([txnid, status, amount, received_hash]):
            logger.warning("Missing webhook fields")
            return HttpResponse("Missing fields", status=400)

        try:
            status = status.strip().lower()
            amount = "{:.2f}".format(float(amount.strip()))
        except Exception:
            logger.warning("Invalid amount or status format")
            return HttpResponse("Invalid data", status=400)

        # Generate hash
        SALT = settings.PAYU_SALT
        KEY = settings.PAYU_KEY

        hash_string = f"{SALT}|{status}|||||||||{amount}|{txnid}|{KEY}"
        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest().lower()

        logger.info("hash_string: %s", hash_string)
        logger.info("calculated_hash: %s", calculated_hash)
        logger.info("received_hash: %s", received_hash)

        # Verify hash
        if calculated_hash != received_hash:
            logger.warning("Hash mismatch in webhook")
            return HttpResponse("Invalid hash", status=400)

        # Update order
        try:
            order = Order.objects.get(transaction_id=txnid)

            if status == "success":
                order.payment_status = "SUCCESS"
            else:
                order.payment_status = "FAILED"

            order.save()
            logger.info(f"Order updated via webhook | order_id={order.id}")

            # Send confirmation email if success
            if status == "success":
                try:
                    from .email_utils import send_order_confirmation_email
                    site_url = request.build_absolute_uri('/')
                    send_order_confirmation_email(order, site_url)
                    logger.info(f"Email sent for order_id={order.id}")
                except Exception as e:
                    logger.error(f"Email failed: {e}")

            return HttpResponse("OK", status=200)

        except Order.DoesNotExist:
            logger.error(f"Order not found for txnid={txnid}")
            return HttpResponse("Order not found", status=404)

    # Handle GET or other methods safely
    logger.info("Webhook endpoint accessed with non-POST request")
    return HttpResponse("Webhook ready", status=200)
 
        


@csrf_exempt
def payment_success(request):
    txnid=request.POST.get("txnid") or request.GET.get("txnid")
    
    if not txnid:
        return redirect('product:home')
    
    try:
        order = Order.objects.get(transaction_id=txnid)
        order.payment_status="SUCCESS"
        order.save()
        
        # Send order confirmation email
        try:
            from .email_utils import send_order_confirmation_email
            site_url = request.build_absolute_uri('/')
            send_order_confirmation_email(order, site_url)
            logger.info(f"Order confirmation email sent for order_id={order.id}")
        except Exception as e:
            logger.error(f"Failed to send order confirmation email: {e}")
        
        return render(request,"product/order_success.html",{"order":order})
    except Order.DoesNotExist:
        logger.error(f"Order not found for txnid={txnid}")
        return redirect('product:home')

@csrf_exempt
def payment_failure(request):
    txnid=request.POST.get("txnid") or request.GET.get("txnid")
    order=Order.objects.filter(transaction_id=txnid).first()


    return render(request, "product/failure.html",{"order":order})




def my_order(request):
    if request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "product/my_order.html", {"orders": orders})


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


# ---------------- WISHLIST ----------------
@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in user's wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, 
        product=product
    )
    
    if not created:
        wishlist_item.delete()
        is_wishlisted = False
    else:
        is_wishlisted = True
    
    return JsonResponse({
        'is_wishlisted': is_wishlisted,
        'wishlist_count': Wishlist.objects.filter(user=request.user).count()
    })

@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'product/wishlist.html', {'wishlist_items': wishlist_items})


# ---------------- FIRST ORDER DISCOUNT ----------------
def is_user_first_order(user):
    """Check if this is user's first successful order"""
    return not Order.objects.filter(user=user, payment_status='SUCCESS').exists()

def apply_first_order_discount(user, amount):
    """Apply 10% discount for first order"""
    if is_user_first_order(user):
        discount = amount * Decimal('0.10')
        return {
            'is_first_order': True,
            'discount_amount': discount,
            'final_amount': amount - discount,
            'original_amount': amount
        }
    return {
        'is_first_order': False,
        'discount_amount': Decimal('0'),
        'final_amount': amount,
        'original_amount': amount
    }

# ---------------- DELIVERY LOCATION ----------------
def validate_delivery_location(address, pincode):
    """Validate if delivery is available to the location"""
    # Only allow delivery to pincode 635109
    return pincode == '635109'
