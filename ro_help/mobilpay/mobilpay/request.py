from xml.dom.minidom import parseString

from mobilpay.mobilpay.payment.request.card import Card
from mobilpay.mobilpay.util.encrypt_data import Crypto


"""
    Request class is the main entry point of the module to create
    payment requests
"""


class Request:

    PAYMENT_TYPE_SMS = "sms"
    PAYMENT_TYPE_CARD = "card"
    PAYMENT_TYPE_TRANSFER = "transfer"
    PAYMENT_TYPE_INTERNET = "homePay"
    PAYMENT_TYPE_BITCOIN = "bitcoin"

    CONFIRM_ERROR_TYPE_NONE = 0
    CONFIRM_ERROR_TYPE_TEMPORARY = 1
    CONFIRM_ERROR_TYPE_PERMANENT = 2

    ERROR_LOAD_X509_CERTIFICATE = 1
    ERROR_ENCRYPT_DATA = 2

    ERROR_PREPARE_MANDATORY_PROPERTIES_UNSET = 1

    ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND = 1
    ERROR_FACTORY_BY_XML_ORDER_TYPE_ATTR_NOT_FOUND = 2
    ERROR_FACTORY_BY_XML_INVALID_TYPE = 3

    ERROR_LOAD_FROM_XML_ORDER_ID_ATTR_MISSING = 0x30000001
    ERROR_LOAD_FROM_XML_SIGNATURE_ELEM_MISSING = 0x30000002

    ERROR_CONFIRM_LOAD_PRIVATE_KEY = 0x300000F0
    ERROR_CONFIRM_FAILED_DECODING_DATA = 0x300000F1
    ERROR_CONFIRM_FAILED_DECODING_ENVELOPE_KEY = 0x300000F2
    ERROR_CONFIRM_FAILED_DECRYPT_DATA = 0x300000F3
    ERROR_CONFIRM_INVALID_POST_METHOD = 0x300000F4
    ERROR_CONFIRM_INVALID_POST_PARAMETERS = 0x300000F5
    ERROR_CONFIRM_INVALID_ACTION = 0x300000F6

    CONFIRM_ERROR_TYPE_NONE = 0
    CONFIRM_ERROR_TYPE_TEMPORARY = 1
    CONFIRM_ERROR_TYPE_PERMANENT = 2

    def __init__(self, payment_type=None, document=None):
        if document is not None:
            self.root_order = document.getElementsByTagName("order")
            self.payment(payment_type, document)
        else:
            self.payment(payment_type)

    def payment(self, payment_type, document=None):
        if payment_type == self.PAYMENT_TYPE_CARD:
            if document is not None:
                return Card(document)
            return Card()

        # TODO ADD OTHER PAYMENT TYPES
        # if payment_type == self.PAYMENT_TYPE_SMS:
        #     if document is not None:
        #         return Card(document)
        #     return Card()

    def factory_from_encrypted(self, env_key, enc_data, private_key_file_path, private_key_password=None):
        private_key = None
        if private_key_password is None:
            private_key = Crypto.get_private_key(private_key_file_path)
        else:
            private_key = Crypto.get_private_key(private_key_file_path, private_key_password)

        if private_key is False:
            raise Exception("Error loading private key", self.ERROR_CONFIRM_LOAD_PRIVATE_KEY)

        # src_data = base64.b64decode(enc_data)
        src_data = enc_data
        if src_data is False:
            raise Exception("Failed decoding data", self.ERROR_CONFIRM_FAILED_DECODING_DATA)

        # src_env_key = base64.b64decode(enc_data)
        src_env_key = env_key
        if src_env_key is False:
            raise Exception("Failed decoding envelope key", self.ERROR_CONFIRM_FAILED_DECODING_ENVELOPE_KEY)

        result = Crypto.decrypt(src_data, private_key, src_env_key)
        if result is False:
            raise Exception("Failed decrypting data", self.ERROR_CONFIRM_FAILED_DECRYPT_DATA)

        try:
            xml_data = parseString(result.decode("utf-8"))
        except:
            raise Exception("Failed decrypting data", self.ERROR_CONFIRM_FAILED_DECRYPT_DATA)

        root_order = xml_data.getElementsByTagName("order")

        if len(root_order) != 1:
            raise Exception(
                "factory_from_xml -> order element not found", self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND
            )

        order = root_order[0]

        attr = order.getAttribute("type")
        if attr is None or len(str(attr)) == 0:
            raise Exception(
                "factory_from_xml -> invalid payment request type={} ".format(attr),
                self.ERROR_FACTORY_BY_XML_ORDER_ELEM_NOT_FOUND,
            )

        if attr == self.PAYMENT_TYPE_CARD:
            obj_pm_req = Card(order)
            return obj_pm_req
        # elif attr == self.PAYMENT_TYPE_SMS:
        #     obj_pm_req = SMS()
        # TODO add other payment types
        else:
            raise Exception(
                "factory_from_xml -> invalid payment request type={} ".format(attr),
                self.ERROR_FACTORY_BY_XML_INVALID_TYPE,
            )
