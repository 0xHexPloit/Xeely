from dataclasses import dataclass
from typing import List

from xeely.custom_xml.entity import XMLEntity


@dataclass(frozen=True)
class XMLDoctype:
    root_name: str
    entities: List[XMLEntity | str]

    def to_xml(self) -> str:
        output = f"<!DOCTYPE {self.root_name} [\n"

        for child in self.entities:
            output += f" {child if isinstance(child, str) else child.to_xml()}\n"

        output += "]>\n"

        return output
