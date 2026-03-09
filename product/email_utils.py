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


def send_order_confirmation_email(order, site_url):
    subject = f"Order Confirmation - {order.product.name}"

    html_message = render_to_string(
        "product/order_confirmation_email.html",
        {
            "order": order,
            "site_url": site_url
        }
    )

    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.user.email],
    )

    email.content_subtype = "html"
    email.send()
