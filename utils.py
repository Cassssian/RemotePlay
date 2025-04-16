# utils.py
# Utility functions: code generation and random usernames

import random
import string
import base64
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def random_username(length=6):
    return 'User_' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def generate_access_code(info: dict) -> str:
    # pack JSON and encrypt with AES, then Base64
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_GCM)
    data = json.dumps(info).encode()
    ct, tag = cipher.encrypt_and_digest(data)
    payload = cipher.nonce + tag + ct + key
    return base64.urlsafe_b64encode(payload).decode()
