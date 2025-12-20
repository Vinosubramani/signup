# product/utils.py
import hashlib

def generate_payu_hash(data, salt):
    hash_string = "|".join(data) + "|" + salt
    return hashlib.sha512(hash_string.encode()).hexdigest().lower()
