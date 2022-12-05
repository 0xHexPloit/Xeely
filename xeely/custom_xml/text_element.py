from dataclasses import dataclass


@dataclass
class XMLTextElement:
    _name: str
    _value: str

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> str:
        return self._value
