from urllib.parse import quote, unquote
from xml.dom.minidom import Document


class Address:
    TYPE_COMPANY = "company"
    TYPE_PERSON = "person"

    ERROR_INVALID_PARAMETER = 0x11100001
    ERROR_INVALID_ADDRESS_TYPE = 0x11100002
    ERROR_INVALID_ADDRESS_TYPE_VALUE = 0x11100003

    def __init__(self, name, contact_info_node=None):
        self._type = None
        self._firstName = None
        self._lastName = None
        self._fiscalNumber = None
        self._identityNumber = None
        self._country = None
        self._county = None
        self._city = None
        self._zipCode = None
        self._address = None
        self._email = None
        self._mobile_phone = None
        self._bank = None
        self._iban = None

        if contact_info_node is not None:
            self.load_from_xml(contact_info_node)

    def load_from_xml(self, billing_node):

        billing_type = billing_node.getAttribute("type")

        if billing_type is not None:
            self._type = billing_node.getAttribute("type")
        else:
            self._type = self.TYPE_PERSON

        try:
            self._firstName = self._check_node(billing_node, "first_name")
            self._lastName = self._check_node(billing_node, "last_name")
            self._fiscalNumber = self._check_node(
                billing_node, "fiscal_number")
            self._identityNumber = self._check_node(
                billing_node, "identity_number")
            self._country = self._check_node(billing_node, "country")
            self._city = self._check_node(billing_node, "city")
            self._zipCode = self._check_node(billing_node, "zip_code")
            self._address = self._check_node(billing_node, "address")
            self._email = self._check_node(billing_node, "email")
            self._mobile_phone = self._check_node(billing_node, "mobile_phone")
            self._bank = self._check_node(billing_node, "bank")
            self._iban = self._check_node(billing_node, "iban")
        except UnicodeEncodeError as e:
            print(e.reason)
            return False

        return True

    def create_xml_element(self, document, name):

        if not isinstance(document, Document):
            raise Exception("ERROR: Invalid document type",
                            self.ERROR_INVALID_PARAMETER)

        if self._type is None:
            raise Exception("ERROR: Invalid address type",
                            self.ERROR_INVALID_ADDRESS_TYPE)

        if self._type.lower() != self.TYPE_PERSON.lower() and self._type.lower() != self.TYPE_COMPANY.lower():
            raise Exception("ERROR: Invalid address type",
                            self.ERROR_INVALID_ADDRESS_TYPE_VALUE)

        xml_address = document.createElement(name)
        xml_address.setAttribute("type", self._type)

        temp = self._create_and_encode_element(
            document, "first_name", self._firstName)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "last_name", self._lastName)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "country", self._country)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(document, "city", self._city)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "zip_code", self._zipCode)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "address", self._address)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(document, "email", self._email)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "mobile_phone", self._mobile_phone)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(document, "bank", self._bank)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(document, "iban", self._iban)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "fiscal_number", self._fiscalNumber)
        if temp is not None:
            xml_address.appendChild(temp)
        temp = self._create_and_encode_element(
            document, "identity_number", self._identityNumber)
        if temp is not None:
            xml_address.appendChild(temp)

        return xml_address

    @staticmethod
    def _create_and_encode_element(document, name, field_text):
        field = document.createElement(name)

        if field_text is not None:
            text = document.createCDATASection(
                quote(field_text, encoding="utf-8"))
            field.appendChild(text)

            return field

    @staticmethod
    def _check_node(node, name):
        tmp_node = node.getElementsByTagName(name)
        if len(tmp_node) > 0:
            if tmp_node[0].firstChild is not None:
                return unquote(tmp_node[0].firstChild.nodeValue, encoding="UTF-8")

    def __str__(self):
        return "[ppiFirstName=" + str(self._firstName) + "]," + \
               "[ppiLastName=" + str(self._lastName) + "]," + \
               "[ppiCountry=" + str(self._country) + "]," + \
               "[ppiCountry=" + str(self._county) + "]," + \
               "[ppiCity=" + str(self._city) + "]," + \
               "[ppiPostalCode=" + str(self._zipCode) + "]," + \
               "[ppiAddress=" + str(self._address) + "]," + \
               "[ppiEmail=" + str(self._email) + "]," + \
               "[ppiPhone=" + str(self._mobile_phone) + "]," + \
               "[ppiBank=" + str(self._bank) + "]," + \
               "[ppiIBAN=" + str(self._iban) + "]," + \
               "[ppiFiscalNumber=" + str(self._fiscalNumber) + "]," + \
               "[ppiIdentityNumber=" + str(self._identityNumber) + "],"

    def set_type(self, billing_type):
        self._type = billing_type

    def set_first_name(self, first_name):
        self._firstName = first_name

    def set_last_name(self, last_name):
        self._lastName = last_name

    def set_address(self, address):
        self._address = address

    def set_email(self, email):
        self._email = email

    def set_mobile_phone(self, mobile_phone):
        self._mobile_phone = mobile_phone
