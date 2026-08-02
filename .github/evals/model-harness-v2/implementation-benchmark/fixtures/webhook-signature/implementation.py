import hashlib, hmac
def verify(secret, body, signature):
    expected = hashlib.sha256(secret + body).hexdigest()
    return expected == signature
