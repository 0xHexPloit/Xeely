from typing import Optional

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import LogsManager
from xeely.custom_xml import XML
from xeely.xxe.attack.handler.abstract import AbstractXXEAttackHandler
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.type import XXEAttackType


class XXEOOBAttackHandler(AbstractXXEAttackHandler):
    def __init__(
        self,
        resource: str,
        xml: XML,
        target_url: str,
        attack_type: XXEAttackType = XXEAttackType.FILE_DISCLOSURE,
        should_use_cdata: bool = False,
        http_server_params: Optional[HTTPServerParams] = None,
    ):
        super().__init__(
            resource=resource,
            target_url=target_url,
            xml=xml,
            attack_type=attack_type,
            attack_mode=XXEAttackMode.OOB,
            should_apply_base64_encoding=True,
            should_use_cdata=should_use_cdata,
            http_server_params=http_server_params,
        )

    def _get_exfiltrated_data(self, **kwargs) -> str:
        latest_log = LogsManager.get_instance().get_latest_log()

        if latest_log is None or "content" not in latest_log:
            return ""

        return latest_log.split("content")[1]
