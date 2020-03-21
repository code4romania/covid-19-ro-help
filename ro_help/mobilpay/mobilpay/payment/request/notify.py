import hashlib
import time
from random import random
from urllib.parse import quote
from datetime import datetime
from mobilpay.mobilpay.address import Address


class Notify:
    ERROR_LOAD_FROM_XML_CRC_ATTR_MISSING = 0x60000001
    ERROR_LOAD_FROM_XML_ACTION_ELEM_MISSING = 0x60000002

    purchaseId = None
    action = None
    errorCode = None
    errorMessage = None
    timestamp = None
    originalAmount = None
    processedAmount = None
    promotionAmount = None
    pan_masked = None
    token_id = None
    token_expiration_date = None
    customer_id = None
    customer_type = None
    customer = None
    issuer = None
    paidByPhone = None
    validationCode = None
    installments = None
    rrn = None

    current_payment_count = 1

    paymentInstrumentId = None

    discounts = []

    _crc = None

    params = []

    def __init__(self, element):
        if element is not None:
            self.load_from_xml(element)

    def load_from_xml(self, element):
        attr = element.getAttribute("timestamp")
        if attr is not None:
            self.timestamp = attr

        attr = element.getAttribute("crc")
        if attr is None:
            raise Exception(
                "Notify -> load_from_xml failed; mandatory crc attribute missing",
                self.ERROR_LOAD_FROM_XML_CRC_ATTR_MISSING,
            )

        self._crc = attr

        elements = element.getElementsByTagName("action")
        if len(elements) != 1:
            raise Exception(
                "Notify -> load_from_xml failed; mandatory action attribute missing",
                self.ERROR_LOAD_FROM_XML_CRC_ATTR_MISSING,
            )

        self.action = elements[0].firstChild.nodeValue

        self.customer = Address("customer", self._get_node_element(element, "customer"))
        self.issuer = self._get_node_element(element, "issuer")
        self.rrn = self._get_node_element(element, "rrn")
        self.purchaseId = self._get_node_element(element, "purchase")
        self.originalAmount = self._get_node_element(element, "original_amount")
        self.processedAmount = self._get_node_element(element, "processed_amount")
        self.promotionAmount = self._get_node_element(element, "promotion_amount")
        self.current_payment_count = self._get_node_element(element, "current_payment_count")
        self.pan_masked = self._get_node_element(element, "pan_masked")
        self.paymentInstrumentId = self._get_node_element(element, "payment_instrument_id")
        self.token_id = self._get_node_element(element, "token_id")
        self.token_expiration_date = self._get_node_element(element, "token_expiration_date")
        self.customer_id = self._get_node_element(element, "customer_id")
        self.paidByPhone = self._get_node_element(element, "paid_by_phone")
        self.validationCode = self._get_node_element(element, "validation_code")
        self.installments = self._get_node_element(element, "installments")

        discounts = self._get_node_element_no_value(element, "discounts")

        if discounts is not None:
            discounts = discounts.getElementsByTagName("discount")

            for discount in discounts:
                temp_discount = {
                    "id": discount.getAttribute("id"),
                    "amount": discount.getAttribute("amount"),
                    "currency": discount.getAttribute("currency"),
                    "third_party": discount.getAttribute("third_party"),
                }
                self.discounts.append(temp_discount)

        elements = self._get_node_element_no_value(element, "error")
        if elements is not None:
            xml_error = elements
            attribute = xml_error.getAttribute("code")
            if attribute is not None:
                self.errorCode = attribute
                self.errorMessage = xml_error.firstChild.nodeValue

    def create_xml_element(self, document):
        xml_notify = document.createElement("mobilpay")
        xml_notify.set("timestamp", f"{datetime.now():%Y%m%d%H%M%S}")

        self._crc = hashlib.md5(str(int(random.random() * int(time.time()))).encode("utf-8")).hexdigest()
        xml_notify.set("crc", self._crc)

        xml_notify.appendChild(self.create_text_element(xml_notify, "action", self.action))

        if isinstance(self.customer, Address):
            xml_notify.appendChild(self.customer.create_xml_element(xml_notify, "customer"))

        xml_notify.appendChild(self.create_text_element(xml_notify, "purchase", self.purchaseId))

        if self.originalAmount is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "original_amount", self.originalAmount))

        if self.processedAmount is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "processed_amount", self.processedAmount))

        if self.promotionAmount is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "promotion_amount", self.promotionAmount))

        if self.current_payment_count is not None:
            xml_notify.appendChild(
                self.create_text_element(xml_notify, "current_payment_count", self.current_payment_count)
            )

        if self.pan_masked is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "pan_masked", self.pan_masked))

        if self.rrn is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "rrn", self.rrn))

        if self.paymentInstrumentId is not None:
            xml_notify.appendChild(
                self.create_text_element(xml_notify, "payment_instrument_id", self.current_payment_count)
            )

        if self.token_id is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "token_id", self.current_payment_count))

        if self.token_expiration_date is not None:
            xml_notify.appendChild(
                self.create_text_element(xml_notify, "token_expiration_date", self.token_expiration_date)
            )

        if self.customer_type is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "customer_type", self.customer_type))

        if self.customer_id is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "customer_id", self.customer_id))

        if self.issuer is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "issuer", self.issuer))

        if self.paidByPhone is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "paid_by_phone", self.paidByPhone))

        if self.validationCode is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "validation_code", self.validationCode))

        if self.installments is not None:
            xml_notify.appendChild(self.create_text_element(xml_notify, "installments", self.installments))

        if len(self.discounts) > 0:
            discounts = xml_notify.createElement("discounts")
            for discount in self.discounts:
                discounts.set("id", discount["id"])
                discounts.set("amount", discount["amount"])
                discounts.set("currency", discount["currency"])
                discounts.set("third_party", discount["third_party"])
                discounts.appendChild(discount)
            xml_notify.appendChild(discounts)

        error_element = xml_notify.createElement("error")
        error_element.set("code", self.errorCode)
        error_text = xml_notify.createCDATASection(quote(self.errorMessage, encoding="utf-8"))
        error_element.appendChild(error_text)

        xml_notify.appendChild(error_element)

        return xml_notify

    @staticmethod
    def create_cdata_element(document, name, value):
        xml_elem = document.createElement(name)
        cdata = document.createCDATASection(quote(value, encoding="UTF-8"))
        xml_elem.appendChild(cdata)
        return xml_elem

    @staticmethod
    def create_text_element(document, name, value):
        xml_elem = document.createElement(name)
        text = document.createTextNode(str(value))
        xml_elem.appendChild(text)
        return xml_elem

    @staticmethod
    def _get_node_element(element, name):
        elements = element.getElementsByTagName(name)
        if len(elements) == 1:
            return elements[0].firstChild.nodeValue
        else:
            return None

    @staticmethod
    def _get_node_element_no_value(element, name):
        elements = element.getElementsByTagName(name)
        if len(elements) == 1:
            return elements[0]
        else:
            return None

    def get_crc(self):
        return self._crc
