from django.utils.crypto import get_random_string
import hashlib

def make_remember_token():
    return get_random_string(48)

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

