from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from product.models import EmailOTP
from product.utils import generate_otp
from product.email_utils import send_otp_email
import logging


logger = logging.getLogger(__name__)

# ---------------- SIGNUP ----------------
def signup(request):
    msg = ""
    show_otp=False

    if request.method == "POST":

        if "signup_submit" in request.POST:
        
            username = request.POST.get('username')
            password = request.POST.get('password')
            password1 = request.POST.get('password1')
            email = request.POST.get("email")
            if User.objects.filter(username=username).exists():
                msg = "Username already exists"
            elif password != password1:
                 msg = "Password and Confirm Password must be the same"
            
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    is_active=False
                )
                user.save()
                
                
                otp = generate_otp()
                EmailOTP.objects.create(user=user, otp=otp)

                send_otp_email(email, otp)  

                request.session["otp_user"] = user.id
                show_otp = True

        elif "otp_submit" in request.POST:
            entered_otp = request.POST.get("otp")
            user_id = request.session.get("otp_user")

            user = User.objects.get(id=user_id)
            email_otp = EmailOTP.objects.get(user=user)

            if email_otp.is_expired():
                msg = "OTP expired"
                show_otp = True

            elif email_otp.otp == entered_otp:
                user.is_active = True
                user.save()
                email_otp.delete()
                return redirect("login")

            else:
                msg = "Invalid OTP"
                show_otp = True

            logger.info(
                "user created|"
                "username=%s | password=%s |email=%s |otp=%s",
                username,password,email,otp
            )

    return render(request, "signup.html", {
        "msg": msg,
        "show_otp": show_otp
    })


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
