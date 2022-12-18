from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract_payload import AbstractBlindPayloadGenerator
from xeely.xxe.attack.payload.factory import payload_factory


@payload_factory.register(name=XXEAttackMode.OOB.value)
class OOBPayloadGenerator(AbstractBlindPayloadGenerator):
    def get_dtd_file_name(self) -> str:
        return "oob.dtd"

    def get_dtd_content(self) -> str:
        return ""

    def generate_payload(self) -> str:
        return ""
