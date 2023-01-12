from dataclasses import dataclass
from typing import Sequence
from typing import Union
from xeely.custom_xml.entity import XMLEntity


@dataclass
class XMLDoctype:
    def __init__(self, root_name: str, entities: Sequence[Union[XMLEntity, str]]):
        self._root_name = root_name
        self._entities = entities

    def to_xml(self) -> str:
        output = f"<!DOCTYPE {self._root_name} [\n"

        for child in self._entities:
            output += f" {child if isinstance(child, str) else child.to_xml()}\n"

        output += "]>"

        return output
