from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


def send_otp_email(to_email, otp):
    subject = "OTP Verification"

    html_message = render_to_string(
        "product/otp_email.html",
        {"otp": otp}   
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )

    email.content_subtype = "html"
    email.send()
