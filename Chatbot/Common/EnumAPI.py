from enum import Enum
from typing import Dict, Optional

from Chatbot.Data.schema import ModuleObject

# Api Information
class ModuleInfo:
    _map: Dict[str, ModuleObject] = {}

    @classmethod
    def set_map(cls, m: Dict[str, ModuleObject]) -> None:
        cls._map = m

    @classmethod
    def get(cls, code: str) -> Optional[ModuleObject]:
        return cls._map.get(code).getUrl()