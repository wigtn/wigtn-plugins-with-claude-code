import unittest, hashlib, hmac
from implementation import verify
class T(unittest.TestCase):
    def test_hmac_sha256(self):
        secret=b"key"; body=b"payload"
        sig=hmac.new(secret,body,hashlib.sha256).hexdigest()
        self.assertTrue(verify(secret,body,sig))
        self.assertFalse(verify(secret,body,sig[:-1]+"0"))
    def test_bad_format(self):
        self.assertFalse(verify(b"k",b"x","not-hex"))
if __name__ == "__main__": unittest.main()
