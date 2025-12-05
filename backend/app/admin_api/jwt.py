import json
import hmac
import time
import base64
from hashlib import sha256

def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

def _b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

def encode(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_enc = _b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    p_enc = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{h_enc}.{p_enc}".encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), signing_input, sha256).digest()
    s_enc = _b64url_encode(sig)
    return f"{h_enc}.{p_enc}.{s_enc}"

def decode(token: str, secret: str) -> dict:
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid token structure')
    h_enc, p_enc, s_enc = parts
    signing_input = f"{h_enc}.{p_enc}".encode('utf-8')
    expected = _b64url_encode(hmac.new(secret.encode('utf-8'), signing_input, sha256).digest())
    if not hmac.compare_digest(expected, s_enc):
        raise ValueError('Invalid signature')
    payload = json.loads(_b64url_decode(p_enc).decode('utf-8'))
    if 'exp' in payload and int(payload['exp']) < int(time.time()):
        raise ValueError('Token expired')
    return payload
