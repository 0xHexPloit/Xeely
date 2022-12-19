from typing import Optional
from urllib.parse import unquote_plus

from xeely.custom_http import HTTPRequest
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.custom_xml.errors import XMLDataNotFound
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.type import XXEAttackType


def get_xml(request_body: str, xml_url_encoded: bool) -> XML:
    if xml_url_encoded:
        if "=" not in request_body:
            raise XMLDataNotFound()
        xml_encoded = request_body.split("=")[1]
        xml = XML.parse_string(unquote_plus(xml_encoded))
    else:
        xml = XML.parse_string(request_body)

    if xml is None:
        raise XMLDataNotFound()

    return xml


def get_payload_prefix(request_body: str, xml_url_encoded: bool) -> str:
    return f"{request_body.split('=')[0]}=" if xml_url_encoded else ""


def get_constructor_params(
    resource: str,
    http_request: HTTPRequest,
    mode: XXEAttackMode = XXEAttackMode.DIRECT,
    xml_urlencoded: bool = False,
    http_server_params: Optional[HTTPServerParams] = None,
    attack_type: XXEAttackType = XXEAttackType.FILE_DISCLOSURE,
    should_apply_base64_encoding: bool = False,
    should_use_cdata: bool = False,
):
    params = {
        "resource": resource,
        "xml": get_xml(http_request.get_body(), xml_url_encoded=xml_urlencoded),
        "target_url": http_request.get_url(),
        "attack_type": attack_type,
        "http_server_params": http_server_params,
        "payload_prefix": get_payload_prefix(
            http_request.get_body(), xml_url_encoded=xml_urlencoded
        ),
        "should_apply_base64_encoding": should_apply_base64_encoding,
        "should_use_cdata": should_use_cdata,
    }

    if mode == XXEAttackMode.OOB:
        del params["should_apply_base64_encoding"]

    return params
