from dataclasses import dataclass
from typing import List

from xeely.custom_xml.entity import XMLEntity


@dataclass
class XMLDoctype:
    _root_name: str
    _entities: List[XMLEntity | str]

    def to_xml(self) -> str:
        output = f"<!DOCTYPE {self._root_name} [\n"

        for child in self._entities:
            output += f" {child if isinstance(child, str) else child.to_xml()}\n"

        output += "]>\n"

        return output
