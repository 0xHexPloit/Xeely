from typing import Any
from typing import Dict
from typing import Type

from xeely.xxe.attack.handler.abstract import AbstractXXEAttackHandler
from xeely.xxe.attack.mode import XXEAttackMode


class XXEAttackHandlerFactory:
    def __init__(self):
        self._handlers: Dict[str, Any] = {}

    def register(self, name: str):
        def decorator_register(cls: Type[AbstractXXEAttackHandler]):
            self._handlers[name] = cls

        return decorator_register

    def get_attack_handler_for_mode(
        self, mode: XXEAttackMode, **kwargs
    ) -> AbstractXXEAttackHandler:
        handler_class = self._handlers.get(str(mode.value))

        if handler_class is None:
            raise ValueError(f"Invalid mode: {mode}")

        instance = handler_class(**kwargs)
        return instance


attack_handler_factory = XXEAttackHandlerFactory()
