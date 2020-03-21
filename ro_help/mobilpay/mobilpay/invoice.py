from decimal import Decimal
from urllib.parse import quote
from locale import LC_ALL, setlocale
from mobilpay.mobilpay.address import Address
from mobilpay.mobilpay.payment.invoice.invoice_item import InvoiceItem


class Invoice:
    def __init__(self, node=None):
        self.ERROR_INVALID_PARAMETER = 0x11110001
        self.ERROR_INVALID_CURRENCY = 0x11110002
        self.ERROR_ITEM_INSERT_INVALID_INDEX = 0x11110003
        self.ERROR_LOAD_FROM_XML_CURRENCY_ATTR_MISSING = 0x31110001
        self.ERROR_LOAD_FROM_XML_AMOUNT_ATTR_MISSING = 0x31110001

        self._currency = None
        self._amount = 0
        self._details = None
        self._installments = None  # default 1
        self._selectedInstallments = None  # default 1
        self._token_id = None

        self._billingAddress = None
        self._shippingAddress = None

        # dom items
        self._items = []

        # exchange rate array
        self._exchangeRates = []
        if node is not None:
            self.load_from_xml(invoice_node=node)

    def load_from_xml(self, invoice_node):

        self._currency = invoice_node.getAttribute("currency")
        if self._currency is None:
            raise Exception(
                "Invoice.load_from_xml failed; currency attribute is missing",
                self.ERROR_LOAD_FROM_XML_CURRENCY_ATTR_MISSING,
            )

        self._amount = invoice_node.getAttribute("amount")
        if self._amount is None:
            raise Exception(
                "Invoice.load_from_xml failed; amount attribute is missing",
                self.ERROR_LOAD_FROM_XML_AMOUNT_ATTR_MISSING,
            )

        self._amount = Decimal(invoice_node.getAttribute("amount"))

        self._token_id = invoice_node.getAttribute("token_id")
        if self._token_id is not None:
            self._token_id = invoice_node.getAttribute("token_id")

        self._installments = invoice_node.getAttribute("installments")
        if self._installments is not None:
            self._installments = invoice_node.getAttribute("installments")

        self._selectedInstallments = invoice_node.getAttribute("selected_installments")
        if self._selectedInstallments is not None:
            self._selectedInstallments = invoice_node.getAttribute("selected_installments")

        details_node = invoice_node.getElementsByTagName("details")
        if len(details_node) == 1:
            self._details = details_node[0].firstChild.nodeValue

        contact_info = invoice_node.getElementsByTagName("contact_info")

        if len(contact_info) == 1:
            address = contact_info[0].getElementsByTagName("billing")
            if len(address) == 1:
                self._billingAddress = Address("billing", address[0])

            address = contact_info[0].getElementsByTagName("shipping")
            if len(address) == 1:
                self._billingAddress = Address("shipping", address[0])

        # items ordered
        invoice_items = invoice_node.getElementsByTagName("items")

        if len(invoice_items) == 1:
            item_elements = invoice_items[0].getElementsByTagName("item")
            if len(item_elements) > 0:
                amount = 0
                for i in item_elements:
                    # print(i)
                    temp_item = InvoiceItem(i)
                    self.add_item(temp_item)
                    amount += temp_item.get_total_amount()
                self._amount = amount
                # print(self._items)

        exchange_rates = invoice_node.getElementsByTagName("exchange_rates")

        if len(exchange_rates) == 1:
            rates_elem = exchange_rates[0].getElementsByTagName("rate")
            if len(rates_elem) > 0:
                for er in rates_elem:
                    self.add_exchange_rate(er)

        return self

    def create_xml_element(self, document):

        invoice_node = document.createElement("invoice")

        if self._currency is None:
            raise Exception("Invalid currency ", self.ERROR_INVALID_CURRENCY)

        invoice_node.setAttribute("currency", self._currency)

        if Decimal(self._amount) > 0:
            setlocale(LC_ALL, "EN_US.UTF-8")

            invoice_node.setAttribute("amount", "{:.2f}".format(Decimal(self._amount)))

        if self._token_id is not None:
            invoice_node.setAttribute("token_id", self._token_id)

        if self._installments is not None and len(self._installments) > 0:
            invoice_node.setAttribute("installments", str(self._installments))

        if self._selectedInstallments is not None and len(self._selectedInstallments) > 0:
            invoice_node.setAttribute("selected_installments", str(self._selectedInstallments))

        if self._details is not None:
            xml_elem = document.createElement("details")
            xml_text = document.createCDATASection(quote(self._details, encoding="utf-8"))
            xml_elem.appendChild(xml_text)
            invoice_node.appendChild(xml_elem)

        contact_info = document.createElement("contact_info")

        if self._billingAddress is not None:
            xml_elem = self._billingAddress.create_xml_element(document, "billing")
            contact_info.appendChild(xml_elem)

        if self._shippingAddress is not None:
            xml_elem = self._shippingAddress.create_xml_element(document, "shipping")
            contact_info.appendChild(xml_elem)

        invoice_node.appendChild(contact_info)

        if self._items is not None and len(self._items) > 0:
            items = document.createElement("items")
            for item in self._items:
                items.append(item.create_xml_document(items))

            invoice_node.append(items)

        return invoice_node

    def add_item(self, item):
        self._items.append(item)

    def add_exchange_rate(self, er):
        if self._exchangeRates is None:
            return
        self._exchangeRates.append(er)

    def get_billing_address(self):
        return self._shippingAddress

    def get_shipping_address(self):
        return self._billingAddress

    def set_shipping_address(self, address):
        self._shippingAddress = address

    def set_billing_address(self, address):
        self._billingAddress = address

    def set_currency(self, currency_type):
        self._currency = currency_type

    def set_amount(self, amount):
        self._amount = amount

    def set_token_id(self, token_id):
        self._token_id = token_id

    def set_details(self, details):
        self._details = details

    def __str__(self):
        return """{0},{1},{2},{3}""".format(self._currency, self._selectedInstallments, self._details, self._amount)
