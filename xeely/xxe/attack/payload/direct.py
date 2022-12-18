from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract import AbstractPayloadGenerator
from xeely.xxe.attack.payload.factory import payload_factory


@payload_factory.register(name=XXEAttackMode.DIRECT.value)
class DirectPayloadGenerator(AbstractPayloadGenerator):
    PLACE_HOLDER: str = "{{XXE}}"

    def generate_payload(self) -> str:

        return (
            super().generate_payload().replace(self.PLACE_HOLDER, f"&{self.MALICIOUS_ENTITY_NAME};")
        )
