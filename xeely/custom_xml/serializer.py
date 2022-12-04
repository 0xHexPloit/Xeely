from typing import Protocol


class XMLSerializer(Protocol):
    def to_xml(self) -> str:
        ...
