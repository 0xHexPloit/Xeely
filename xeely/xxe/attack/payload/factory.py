from typing import Any
from typing import Dict
from typing import Type

from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract import AbstractPayloadGenerator


class XXEPayloadGeneratorFactory:
    _attacks: Dict[str, Any]

    def __init__(self):
        self._attacks = {}

    def register(self, name: str):
        def decorator_register(cls: Type[AbstractPayloadGenerator]):
            self._attacks[name] = cls

        return decorator_register

    def get_payload_generator_for_mode(
        self, mode: XXEAttackMode, **kwargs
    ) -> AbstractPayloadGenerator:
        payload_class = self._attacks.get(str(mode.value))

        if payload_class is None:
            raise ValueError(f"Invalid mode: {mode}")

        instance = payload_class(**kwargs)
        return instance


payload_factory = XXEPayloadGeneratorFactory()
