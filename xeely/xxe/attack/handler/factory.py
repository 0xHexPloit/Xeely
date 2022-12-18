from typing import Any
from typing import Dict
from typing import Type

from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload.abstract import AbstractPayloadGenerator


class XXEAttackHandlerFactory:
    def __init__(self):
        self._handlers: Dict[str, Any] = {}

    def register(self, name: str):
        def decorator_register(cls: Type[AbstractPayloadGenerator]):
            self._handlers[name] = cls

        return decorator_register

    def get_attack_handler_for_mode(
        self, mode: XXEAttackMode, **kwargs
    ) -> AbstractPayloadGenerator:
        handler_class = self._handlers.get(str(mode.value))

        if handler_class is None:
            raise ValueError(f"Invalid mode: {mode}")

        instance = handler_class(**kwargs)
        return instance


attack_handler_factory = XXEAttackHandlerFactory()
