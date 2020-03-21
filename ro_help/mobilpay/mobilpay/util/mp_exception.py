class ErrorCodes:
    INVALID_TYPE_EXCEPTION = 0x11111
    INVALID_VALUE_EXCEPTION = 0x12345


class MPException(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return repr(self.code)


try:
    raise MPException(ErrorCodes.INVALID_TYPE_EXCEPTION)
except MPException as e:
    print("Received error with code:", e.code)


