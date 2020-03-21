from mobilpay.mobilpay.payment.request.base_request import BaseRequest
from mobilpay.mobilpay.invoice import Invoice
from datetime import datetime
from xml.dom.minidom import Document


class Card(BaseRequest):
    ERROR_LOAD_FROM_XML_ORDER_INVOICE_ELEM_MISSING = 0x30000001

    def __init__(self, root_document=None):
        super().__init__()

        self._invoice = Invoice()
        self._type = "card"

        if root_document is not None:
            self._load_from_xml(root_document)

    def _load_from_xml(self, element):
        super()._parse_from_xml(element)

        elems = element.getElementsByTagName("invoice")
        if len(elems) != 1:
            raise Exception("Card -> load_from_xml failed; invoice element is missing ",
                            self.ERROR_LOAD_FROM_XML_ORDER_INVOICE_ELEM_MISSING)

        self._invoice = Invoice(elems[0])

        return self

    def encrypt(self, x509_file_path):
        if self._signature is None or self._orderId is None or isinstance(self._invoice, Invoice) is not True:
            raise Exception("One or more mandatory properties are invalid!: " +
                            str(self._signature) + ":" + str(self._orderId), self.ERROR_PREPARE_MANDATORY_PROPERTIES_UNSET)

        xml_doc = Document()

        order = xml_doc.createElement("order")

        order.setAttribute("type", self._type)
        order.setAttribute("id", self._orderId)

        order.setAttribute("timestamp", f"{datetime.now():%Y%m%d%H%M%S}")

        signature = xml_doc.createElement("signature")
        signature_text = xml_doc.createTextNode(self._signature)
        signature.appendChild(signature_text)

        invoice = self._invoice.create_xml_element(xml_doc)

        order.appendChild(signature)
        order.appendChild(invoice)

        if self._objRequestParams is not None and len(self._objRequestParams) > 0:
            params = xml_doc.createElement("params")
            for p in self._objRequestParams:
                param = xml_doc.createElement("param")
                name = xml_doc.createElement("name")
                value = xml_doc.createElement("value")
                name_text = xml_doc.createTextNode(p.strip())
                value_text = xml_doc.createCDATASection(
                    self._objRequestParams.get(p))
                name.appendChild(name_text)
                value.appendChild(value_text)
                param.appendChild(name)
                param.appendChild(value)
                params.appendChild(param)

            xml_doc.appendChild(params)

        if self._returnUrl is not None and len(self._returnUrl) > 0:
            url = xml_doc.createElement("url")
            return_url = xml_doc.createElement("return")
            return_url_text = xml_doc.createTextNode(self._returnUrl)
            return_url.appendChild(return_url_text)
            url.appendChild(return_url)
            if self._confirmUrl is not None and len(self._confirmUrl) > 0:
                confirm_url = xml_doc.createElement("confirm")
                confirm_url_text = xml_doc.createTextNode(self._confirmUrl)
                confirm_url.appendChild(confirm_url_text)
                url.appendChild(confirm_url)

            order.appendChild(url)

        xml_doc.appendChild(order)
        self._xmlDoc = xml_doc
        super()._encrypt(x509_file_path)

    def set_confirm_url(self, confirm_url):
        self._confirmUrl = confirm_url

    def set_return_url(self, return_url):
        self._returnUrl = return_url

    def set_invoice(self, invoice):
        self._invoice = invoice

    def get_invoice(self):
        return self._invoice

    def set_payment_type(self, payment_type):
        self._type = payment_type

    def __str__(self):
        return super().__str__() + " " + self._returnUrl
