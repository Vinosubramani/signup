from django.urls import path
from .views import user_login, logout_view, signup,verify_otp,resend_otp

urlpatterns = [
    path("login/", user_login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup, name="signup"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),

]
