"""
    Client side / Front End
    Path of the imports should be changed according to the location of the module in your project
"""

from urllib.parse import unquote, quote
import requests
import hashlib
import random
import time
from mobilpay.mobilpay.address import Address
from mobilpay.mobilpay.invoice import Invoice
from mobilpay.mobilpay.request import Request
from mobilpay.mobilpay.payment.request.crc import Crc
from mobilpay.mobilpay.payment.request.card import Card
from mobilpay.mobilpay.payment.request.base_request import BaseRequest
from django.conf import settings

# implementation example


def get_and_send_request(base_url, order):
    obj_pm_req_card = Card()

    try:
        obj_pm_req_card.set_signature(order.ngo.mobilpay_icc)
        # obj_pm_req_card.set_signature(iid)

        # order id
        obj_pm_req_card.set_order_id(order.order_id)
        obj_pm_req_card.set_confirm_url(f"{base_url}/ro/mobilpay/confirm/{order.order_id}")
        obj_pm_req_card.set_return_url(f"{base_url}/ro/mobilpay/response/{order.order_id}")
        obj_pm_req_card.set_invoice(Invoice())
        obj_pm_req_card.get_invoice().set_currency("RON")
        obj_pm_req_card.get_invoice().set_amount(f"{order.amount:.2f}")
        obj_pm_req_card.get_invoice().set_token_id(order.ngo.mobilpay_icc)
        if order.details:
            details = order.details
        else:
            details = f"Donatie catre {order.ngo.name}"
        obj_pm_req_card.get_invoice().set_details(details)
        billing_address = Address("billing")

        # get_from_website
        billing_address.set_type("person")
        billing_address.set_first_name(order.first_name)
        billing_address.set_last_name(order.last_name)
        billing_address.set_address(order.address)
        billing_address.set_email(order.email)
        billing_address.set_mobile_phone(order.phone)

        obj_pm_req_card.get_invoice().set_billing_address(billing_address)

        # shipping_address = Address("shipping")
        # # get_from_website
        # shipping_address.set_type("person")
        # shipping_address.set_first_name("Netopia")
        # shipping_address.set_last_name("Payments")
        # shipping_address.set_address("Pipera")
        # shipping_address.set_email("contact@netopia.com")
        # shipping_address.set_mobile_phone("8989989")

        # obj_pm_req_card.get_invoice().set_shipping_address(shipping_address)

        """encoded data and env_key"""
        obj_pm_req_card.encrypt(order.ngo.mobilpay_public_key.path)
        data = obj_pm_req_card.get_enc_data()
        env_key = obj_pm_req_card.get_env_key()

        return data, env_key

    except Exception as e:
        raise Exception(e)
