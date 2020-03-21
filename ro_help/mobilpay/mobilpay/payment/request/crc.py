from xml.dom.minidom import Document


class Crc():
    def __init__(self, error_code, error_type, error_message):
        """
            error_code, error_type, error_message
        """
        self.error_code = error_code
        self.error_type = error_type
        self.error_message = error_message

    def create_crc(self):
        crc = Document()
        crc_text = crc.createElement("crc")
        crc_value = crc.createTextNode(self.error_message)

        if self.error_code != 0:
            crc_text.setAttribute("error_type", str(self.error_type))
            crc_text.setAttribute("error_code", str(self.error_code))

        crc_text.appendChild(crc_value)
        crc.appendChild(crc_text)
        return crc
