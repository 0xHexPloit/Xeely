from pathlib import Path

import pytest

from xeely.custom_http.errors import HTTPFieldMissingException
from xeely.custom_http.errors import HTTPRequestParsingException
from xeely.custom_http.request import HTTPRequest

resources_path = Path("..").resolve() / "resources"


def test_parsing_valid_request_with_body_data():
    valid_request_path = resources_path / "valid_request.txt"
    with open(valid_request_path) as file:
        data = file.read()
        request = HTTPRequest.parse_request(data)

        url = request.get_url()
        body = request.body

        assert url == "http://127.0.0.1/api/hello"
        assert body == "BODY DATA"


def test_parsing_valid_request_with_empty_body():
    valid_request_path = resources_path / "request_with_empty_body.txt"

    with open(valid_request_path) as file:
        data = file.read()
        request = HTTPRequest.parse_request(data)
        body = request.body

        assert body == ""


def test_parsing_with_invalid_method():
    invalid_request_path = resources_path / "request_invalid_method.txt"
    with open(invalid_request_path) as file:
        data = file.read()

        with pytest.raises(HTTPRequestParsingException):
            HTTPRequest.parse_request(data)


def test_parsing_with_invalid_path():
    invalid_request_path = resources_path / "request_invalid_path.txt"

    with open(invalid_request_path) as file:
        data = file.read()

        with pytest.raises(HTTPRequestParsingException):
            HTTPRequest.parse_request(data)


def test_getting_url_with_missing_host_raises_exception():
    invalid_request_path = resources_path / "request_with_missing_host.txt"

    with open(invalid_request_path) as file:
        data = file.read()

        with pytest.raises(HTTPFieldMissingException):
            request = HTTPRequest.parse_request(data)
            request.get_url()
