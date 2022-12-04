class HTTPRequestParsingException(Exception):
    def __init__(self):
        super().__init__("Failed to parse HTTP request")
