from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from product.models import EmailOTP
from product.utils import generate_otp, get_expiry
from product.email_utils import send_otp_email
import logging

logger = logging.getLogger(__name__)


# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password1 = request.POST["password1"]

        logger.info(f"Signup attempt | username={username} | email={email}")

        if password != password1:
            logger.warning(f"Signup failed - Password mismatch | username={username} | email={email}")
            return render(request, "signup.html", {"msg": "Passwords do not match"})

       
        otp = generate_otp()
        expiry = get_expiry()

        EmailOTP.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "expires_at": expiry}
        )

        logger.info(f"OTP generated and sent | email={email} | otp={otp}")
        send_otp_email(email, otp)

       
        request.session["signup_data"] = {
            "username": username,
            "email": email,
            "password": password,
        }

        logger.info(f"Signup data stored in session | username={username} | email={email}")
        return redirect("verify_otp")

    return render(request, "signup.html")


def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST["otp"]
        signup_data = request.session.get("signup_data")

        if not signup_data:
            logger.warning("OTP verification failed - No signup data in session")
            return redirect("signup")

        email = signup_data["email"]
        username = signup_data["username"]

        logger.info(f"OTP verification attempt | username={username} | email={email} | entered_otp={entered_otp}")

        otp_obj = EmailOTP.objects.filter(email=email).first()

        if not otp_obj:
            logger.warning(f"OTP verification failed - OTP not found | email={email}")
            return render(request, "verify_otp.html", {"msg": "OTP not found"})

        if otp_obj.is_expired():
            logger.warning(f"OTP verification failed - OTP expired | email={email}")
            return render(request, "verify_otp.html", {"msg": "OTP expired"})

        if otp_obj.otp != entered_otp:
            logger.warning(f"OTP verification failed - Invalid OTP | email={email} | expected={otp_obj.otp} | entered={entered_otp}")
            return render(request, "verify_otp.html", {"msg": "Invalid OTP"})

        
        user = User.objects.create_user(
            username=signup_data["username"],
            email=email,
            password=signup_data["password"]
        )

        logger.info(f"User created successfully | user_id={user.id} | username={username} | email={email}")

        otp_obj.delete()
        del request.session["signup_data"]

        logger.info(f"Signup completed successfully | username={username} | email={email}")
        return redirect("login")

    return render(request, "verify_otp.html")


def resend_otp(request):
    signup_data = request.session.get("signup_data")

    if not signup_data:
        logger.warning("Resend OTP failed - No signup data in session")
        return redirect("signup")

    email = signup_data["email"]
    username = signup_data.get("username", "unknown")
    otp = generate_otp()
    expiry = get_expiry()

    EmailOTP.objects.update_or_create(
        email=email,
        defaults={"otp": otp, "expires_at": expiry}
    )

    logger.info(f"OTP resent | username={username} | email={email} | new_otp={otp}")
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
