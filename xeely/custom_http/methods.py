from enum import Enum
from typing import Optional


class HTTPMethods(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"

    @staticmethod
    def get_method_from_raw_data(data: str) -> Optional["HTTPMethods"]:
        match = [method for method in HTTPMethods if method.value == data.upper()]
        return match[0] if len(match) == 1 else None
