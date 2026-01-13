# services.py
import requests
from django.conf import settings

# services.py
import requests
from django.conf import settings

def send_otp_email(email, otp):
    payload = {
        "service_id": settings.EMAILJS_SERVICE_ID,
        "template_id": settings.EMAILJS_TEMPLATE_ID,

        # BOTH keys are required
        "user_id": settings.EMAILJS_PUBLIC_KEY,      # ✅ Public key
        "accessToken": settings.EMAILJS_PRIVATE_KEY, # ✅ Private key

        "template_params": {
            "to_email": email,
            "otp": otp
        }
    }

    response = requests.post(
        "https://api.emailjs.com/api/v1.0/email/send",
        json=payload
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
