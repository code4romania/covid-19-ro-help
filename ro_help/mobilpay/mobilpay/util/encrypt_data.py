from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from Crypto.Cipher import ARC4
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from OpenSSL import crypto
import base64


class Crypto:

    @staticmethod
    def get_private_key(file_path, password=None):
        private_key = RSA.importKey(
            open(file_path, 'r').read(), passphrase=password)
        return private_key

    @staticmethod
    def get_rsa_key(file_path):
        # Importing keys from files, converting it into the RsaKey object

        # this is used for certs
        cert_data = crypto.load_certificate(
            crypto.FILETYPE_PEM, open(file_path, 'r').read().encode("utf-8"))
        public_key_object = cert_data.get_pubkey()
        public_key_string = crypto.dump_publickey(
            crypto.FILETYPE_PEM, public_key_object)
        public_key = RSA.importKey(public_key_string.decode("utf-8"))

        # this is used for local keys
        # public_key = RSA.importKey(open(file_path, 'r').read())

        return public_key

    @staticmethod
    def encrypt(src_data, public_key):
        random_key = Random.new().read(16)

        cipher = PKCS1_v1_5.new(public_key)
        enc_key = cipher.encrypt(random_key)
        cipher = ARC4.new(random_key)
        enc_data = cipher.encrypt(src_data)
        enc_data = base64.b64encode(enc_data)
        enc_key = base64.b64encode(enc_key)

        # decode because the byte string because is not accepted by the server
        return enc_data.decode('utf-8'), enc_key.decode('utf-8')

    @staticmethod
    def decrypt(enc_data, private_key, enc_key):
        # encode because the b64decode is taking a byte string as an argument
        ERROR_ENV_DATA_MISSING = 0x300001f1
        try:
            enc_data = base64.b64decode(enc_data)
            enc_key = base64.b64decode(enc_key)
        except:
            raise Exception("Failed decoding enc_data and enc_key",
                            ERROR_ENV_DATA_MISSING)

        try:
            decrypt = PKCS1_v1_5.new(private_key)
            decrypted_key = decrypt.decrypt(enc_key, Random.new().read(16))
            cipher = ARC4.new(decrypted_key)
            xml_data = cipher.decrypt(enc_data)
            return xml_data
        except:
            raise Exception("Failed decrypting data",
                            ERROR_ENV_DATA_MISSING)
