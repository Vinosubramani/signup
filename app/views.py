from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from product.models import EmailOTP
from product.utils import generate_otp, get_expiry
from product.email_utils import send_otp_email


# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password1 = request.POST["password1"]

        if password != password1:
            return render(request, "signup.html", {"msg": "Passwords do not match"})

       
        otp = generate_otp()
        expiry = get_expiry()

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry}
        )

        send_otp_email(email, otp)

       
        request.session["signup_data"] = {
            "username": username,
            "email": email,
            "password": password,
        }

        
        return redirect("verify_otp")

    return render(request, "signup.html")


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST["otp"]
        signup_data = request.session.get("signup_data")

        if not signup_data:
            return redirect("signup")

        email = signup_data["email"]

        otp_obj = EmailOTP.objects.filter(email=email).first()

        if not otp_obj:
            return render(request, "verify_otp.html", {"msg": "OTP not found"})

        if otp_obj.is_expired():
            return render(request, "verify_otp.html", {"msg": "OTP expired"})

        if otp_obj.otp != entered_otp:
            return render(request, "verify_otp.html", {"msg": "Invalid OTP"})

        
        User.objects.create_user(
            username=signup_data["username"],
            email=email,
            password=signup_data["password"]
        )

        otp_obj.delete()
        del request.session["signup_data"]

        return redirect("login")

    return render(request, "verify_otp.html")


def resend_otp(request):
    signup_data = request.session.get("signup_data")

    if not signup_data:
        return redirect("signup")

    email = signup_data["email"]
    otp = generate_otp()
    expiry = get_expiry()

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={"otp": otp, "expires_at": expiry}
    )

    send_otp_email(email, otp)

    messages.success(request, "OTP sent again successfully")
    return redirect("verify_otp")


# ---------------- LOGIN ----------------
def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # SUPERUSER
            if user.is_superuser:
                return redirect('/master-admin/')

            # STAFF
            elif user.is_staff:
                return redirect('/staff/')

            # NORMAL USER
            else:
                return redirect('product:home')   

        return render(request, 'login.html', {
            'error': 'Invalid Username or Password!'
        })

    return render(request, 'login.html')


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect('login')
