import time

import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request
from werkzeug import Response

from xeely.custom_http.client import HTTPClient
from xeely.custom_http.errors import ClientStatusException
from xeely.custom_http.errors import ClientTimeoutException


def handle_post_request(request: Request):
    body_data = request.data
    return Response(f"Hello, {body_data.decode('utf-8')}")


def timeout_handler(request: Request):
    time.sleep(2)
    return Response("")


def test_get_hello_with_correct_name(httpserver: HTTPServer):
    first_name = "Jean"
    httpserver.expect_request(uri="/", method="POST").respond_with_handler(handle_post_request)
    resp = HTTPClient.send_post_request(f"http://localhost:{httpserver.port}/", first_name)

    assert resp.body == f"Hello, {first_name}"


def test_status_code_exception_rising(httpserver: HTTPServer):
    httpserver.expect_request(uri="/", method="POST").respond_with_data(status=400)

    with pytest.raises(ClientStatusException):
        HTTPClient.send_post_request(f"http://localhost:{httpserver.port}/", "")


def test_timeout_exception_rising(httpserver: HTTPServer):
    httpserver.expect_request(uri="/", method="POST").respond_with_handler(timeout_handler)

    with pytest.raises(ClientTimeoutException):
        HTTPClient.send_post_request(f"http://localhost:{httpserver.port}/", "", timeout=1)
