from typing import Any
from typing import Dict
from typing import Type

from xeely.xxe.attacks.base import BaseXXEAttack


class XXEAttacksFactory:
    _attacks: Dict[str, Any]

    def __init__(self):
        self._attacks = {}

    def register(self, name: str):
        def decorator_register(cls: Type[BaseXXEAttack]):
            self._attacks[name] = cls

        return decorator_register

    def create_attack_instance_for_strategy(self, strategy: str, **kwargs) -> BaseXXEAttack:
        attack_class = self._attacks.get(strategy)

        if attack_class is None:
            raise ValueError(f"Invalid strategy: {strategy}")

        instance: BaseXXEAttack = attack_class(**kwargs)
        return instance


factory = XXEAttacksFactory()
