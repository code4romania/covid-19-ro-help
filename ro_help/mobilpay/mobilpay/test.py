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
    def test_self_roundtrip(self):
        pubkey = Crypto().get_rsa_key('pki/us-rsa1024/public.pem')
        privkey = Crypto().get_private_key('pki/us-rsa1024/private.pem')
        clear_msg = b'forty-two'
        enc_msg, enc_block_key = Crypto().encrypt(clear_msg, pubkey)
        dec_msg = Crypto().decrypt(enc_msg, privkey, enc_block_key)
        self.assertEqual(dec_msg, clear_msg)
    def test_decrypt(self):
        d = 'pki/them-rsa1024/'
        def _slurp(fname):
            with open(d + fname, 'r') as fp:
                return fp.read()

        msg_enc = _slurp('msg.enc.b64')
        enc_key_rsaenc = _slurp('enc.key.rsaenc.b64')
        privkey = Crypto().get_private_key(d + 'private.pem')
        dec_msg = Crypto().decrypt(msg_enc, privkey, enc_key_rsaenc)
        self.assertEqual(dec_msg, b'message from them\n')

if __name__ == "__main__":
    unittest.main()
