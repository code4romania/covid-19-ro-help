#!/usr/bin/env python3

import unittest
from mobilpay.mobilpay.util.encrypt_data import Crypto

class TestCrypto(unittest.TestCase):
    def test_load_pub(self):
        pubkey = Crypto().get_rsa_key('pki/us-rsa1024/public.pem')
        self.assertIsNotNone(pubkey)
        self.assertTrue(pubkey)
    def test_load_priv(self):
        privkey = Crypto().get_private_key('pki/us-rsa1024/private.pem')
        self.assertIsNotNone(privkey)
        self.assertTrue(privkey)

if __name__ == "__main__":
    unittest.main()
