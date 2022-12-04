class HTTPFieldMissingException(Exception):
    def __init__(self, field_name: str):
        super().__init__(f"The filed: '{field_name}' is missing")
