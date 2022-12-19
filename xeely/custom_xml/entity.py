class XMLEntity:
    def __init__(
        self, name: str, value: str, is_external: bool = False, is_parameter: bool = False
    ):
        self._name = name
        self._value = value
        self._is_external = is_external
        self._is_parameter = is_parameter

    def to_xml(self) -> str:
        output = "<!ENTITY"

        if self._is_parameter:
            output += " %"

        output += f" {self._name}"

        if self._is_external:
            output += " SYSTEM"

        output += f' "{self._value}">'

        return output
