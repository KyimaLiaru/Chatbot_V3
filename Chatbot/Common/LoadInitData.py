import re

from enum import Enum
from typing import Dict, Optional, Iterable, List, Tuple

from Chatbot.Data.schema import ModuleObject, PatternObject


# Api Information
class ModuleInfo:
    _map: Dict[str, ModuleObject] = {}

    @classmethod
    def set_map(cls, m: Dict[str, ModuleObject]) -> None:
        cls._map = m

    @classmethod
    def get(cls, code: str) -> Optional[ModuleObject]:
        return cls._map.get(code).getUrl()

class PatternInfo:
    _patterns: List[Tuple[int, str, re.Pattern]] = []

    @classmethod
    def set_list(cls, items: List[PatternObject]) -> None:
        result: List[Tuple[int, str, re.Pattern]] = []

        for item in items:
            result.append(item.getPattern())

        cls._patterns = result

    @classmethod
    def replaceTokens(cls, text: str) -> str:
        for idx, name, pattern in cls._patterns:
            text = pattern.sub(f"<{name}>", text)
        return text

    # @classmethod
    # def get(cls) ->  Dict[int, Dict[str, re.Pattern]]:
    #     return cls._patterns