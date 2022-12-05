from dataclasses import dataclass


@dataclass
class XMLEntity:
    _name: str
    _value: str
    _is_external: bool = False
    _is_parameter: bool = False

    def to_xml(self) -> str:
        output = "<!ENTITY"

        if self._is_parameter:
            output += " %"

        output += f" {self._name}"

        if self._is_external:
            output += " SYSTEM"

        output += f' "{self._value}">'

        return output
