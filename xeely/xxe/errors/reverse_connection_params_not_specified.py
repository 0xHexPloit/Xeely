from .invalid_option import InvalidOptionException


class ReverseConnectionParamsNotSpecified(InvalidOptionException):
    def __init__(self):
        super().__init__("lhost")
