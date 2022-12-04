from dataclasses import dataclass


@dataclass(frozen=True)
class XMLEntity:
    name: str
    value: str
    is_external: bool = False
    is_parameter: bool = False

    def to_xml(self) -> str:
        output = "<!ENTITY"

        if self.is_parameter:
            output += " %"

        output += f" {self.name}"

        if self.is_external:
            output += " SYSTEM"

        output += f' "{self.value}">'

        return output
