
import hashlib

def generate_hash(key, salt, txnid, amount, productinfo, firstname, email):
    hash_string = (
        f"{key}|{txnid}|{amount}|{productinfo}|"
        f"{firstname}|{email}|||||||||||{salt}"
    )

    return hashlib.sha512(hash_string.encode()).hexdigest().lower()
