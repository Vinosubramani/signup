import hashlib
import random
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

def apply_product_search(products, search_query):
    if search_query:
        products=products.filter(
            Q(name__icontains=search_query)
        )
        return products




def generate_payu_hash(data, salt):
    hash_string = "|".join(data) + "|" + salt
    return hashlib.sha512(hash_string.encode()).hexdigest().lower()




def generate_otp():
    return str(random.randint(100000, 999999))

otp = generate_otp()
# print("Generated OTP:", otp)


def get_expiry():
    return timezone.now() + timedelta(minutes=2)