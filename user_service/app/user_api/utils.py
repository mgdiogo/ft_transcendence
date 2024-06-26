import os
import hmac
import json
import base64
import hashlib

SECRET_KEY = os.getenv('SECRET_KEY')

def base64_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64_decode(data):
    return base64.urlsafe_b64decode(data + b'=' * (-len(data % 4)))

def generate_jwt(payload, secret=SECRET_KEY):
    header = json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode()
    payload = json.dumps(payload).encode()

    header_encoded = base64_encode(header)
    payload_encoded = base64_encode(payload)

    signature = hmac.new(secret.encode(), f'{header_encoded}.{payload_encoded}'.encode(), hashlib.sha256).digest()
    signature_encoded = base64_encode(signature)

    return f'{header_encoded}.{payload_encoded}.{signature_encoded}'

def decode_jwt(token, secret=SECRET_KEY):
    header_encoded, payload_encoded, signature_encoded = token.split('.')

    signature = hmac.new(secret.encode(), f'{header_encoded}.{payload_encoded}'.encode(), hashlib.sha256).digest()
    signature_check = base64_encode(signature)

    if signature_check != signature_encoded:
        raise ValueError('Invalid signature')
    
    payload = base64_decode(payload_encoded)
    return json.loads(payload)