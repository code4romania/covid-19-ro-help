from urllib.parse import quote, unquote
from decimal import Decimal
from xml.dom.minidom import Document


class InvoiceItem:
    ERROR_INVALID_PARAMETER = 0x11111001
    ERROR_INVALID_PROPERTY = 0x11110002

    ERROR_LOAD_FROM_XML_CODE_ELEM_MISSING = 0x40000001
    ERROR_LOAD_FROM_XML_NAME_ELEM_MISSING = 0x40000002
    ERROR_LOAD_FROM_XML_QUANTITY_ELEM_MISSING = 0x40000003
    ERROR_LOAD_FROM_XML_QUANTITY_ELEM_EMPTY = 0x40000004
    ERROR_LOAD_FROM_XML_PRICE_ELEM_MISSING = 0x40000005
    ERROR_LOAD_FROM_XML_PRICE_ELEM_EMPTY = 0x40000006
    ERROR_LOAD_FROM_XML_VAT_ELEM_MISSING = 0x40000007

    def __init__(self, items_node):
        self._code = None
        self._name = None
        self._measurement = None
        self._quantity = 0
        self._price = 0
        self._vat = 0

        if items_node is not None:
            try:
                self.load_from_xml(items_node)
            except IOError as ioe:
                print(ioe)

    def load_from_xml(self, item_node):

        xml_temp = item_node.getElementsByTagName("code")
        if len(xml_temp) != 1:
            raise Exception("load_from_xml -> Invalid code element",
                            self.ERROR_LOAD_FROM_XML_CODE_ELEM_MISSING)
        self._code = unquote(
            xml_temp[0].firstChild.nodeValue, encoding="utf-8")

        xml_temp = item_node.getElementsByTagName("name")
        if len(xml_temp) != 1:
            raise Exception("load_from_xml -> Invalid name element",
                            self.ERROR_LOAD_FROM_XML_NAME_ELEM_MISSING)
        self._name = unquote(
            xml_temp[0].firstChild.nodeValue, encoding="utf-8")

        xml_temp = item_node.getElementsByTagName("measurement")
        if len(xml_temp) == 1:
            self._measurement = unquote(
                xml_temp[0].firstChild.nodeValue, encoding="UTF-8")

        xml_temp = item_node.getElementsByTagName("quantity")
        if len(xml_temp) != 1:
            raise Exception(
                "load_from_xml -> Invalid quantity element", self.ERROR_LOAD_FROM_XML_QUANTITY_ELEM_MISSING)

        self._quantity = Decimal(
            unquote(xml_temp[0].firstChild.nodeValue, encoding="UTF-8"))

        if self._quantity <= 0:
            raise Exception("load_from_xml -> Invalid quantity value: " + str(self._quantity),
                            self.ERROR_LOAD_FROM_XML_QUANTITY_ELEM_EMPTY)

        xml_temp = item_node.getElementsByTagName("price")
        if len(xml_temp) != 1:
            raise Exception("load_from_xml -> Invalid price element",
                            self.ERROR_LOAD_FROM_XML_PRICE_ELEM_MISSING)

        self._price = Decimal(
            unquote(xml_temp[0].firstChild.nodeValue, encoding="UTF-8"))

        if self._price < 0:
            raise Exception("load_from_xml -> Invalid quantity value: " + str(self._price),
                            self.ERROR_LOAD_FROM_XML_PRICE_ELEM_EMPTY)

        xml_temp = item_node.getElementsByTagName("vat")

        if len(xml_temp) != 1:
            raise Exception("load_from_xml -> Invalid vat element",
                            self.ERROR_LOAD_FROM_XML_VAT_ELEM_MISSING)

        self._vat = Decimal(unquote(xml_temp[0].firstChild.nodeValue))

        return True

    def create_xml_document(self, document):

        if (document is None) and isinstance(document, Document) is False:
            raise Exception("Invalid property", self.ERROR_INVALID_PARAMETER)

        xml_item = document.createElement("item")

        if (
                self._code is None or
                self._name is None or
                self._measurement is None or
                self._quantity is None or
                self._price is None or
                self._vat is None
        ):
            raise Exception("Invalid property", self.ERROR_INVALID_PROPERTY)

        xml_item.appendChild(self.create_cdata_element(
            document, "code", self._code))
        xml_item.appendChild(self.create_cdata_element(
            document, "name", self._name))
        xml_item.appendChild(self.create_cdata_element(
            document, "measurement", self._measurement))
        xml_item.appendChild(self.create_text_element(
            document, "quantity", self._quantity))
        xml_item.appendChild(self.create_text_element(
            document, "price", self._price))
        xml_item.appendChild(self.create_text_element(
            document, "vat", self._vat))

        return xml_item

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

    def __str__(self):
        return str(self._code) + " " + \
            str(self._name) + " " + \
            str(self._measurement) + " " + \
            str(self._quantity) + " " + \
            str(self._price) + " " + \
            str(self._vat)

    def get_total_amount(self):
        value = round(self._price * self._quantity, 2)
        vat = round(value * self._vat, 2)
        return value + vat
