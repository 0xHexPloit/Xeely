from dataclasses import dataclass


@dataclass(frozen=True)
class XMLTextElement:
    name: str
    value: str
