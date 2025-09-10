from enum import Enum
from typing import Dict, Optional

from Data.schema import ModuleObject


# API Url Enumerations (DB 연결 필요?)
class ApiInfo(Enum):
    ARGOS_FIREWALLAPI = "http://192.168.7.178:8081/"
    ARGOS_WEB = "http://localhost:8190/"
    ARGOS_COMMON = "http://localhost:8191/"
    ARGOS_APPROVAL = "http://localhost:8192/"
    ARGOS_PUSH = "http://localhost:8193/"
    ARGOS_POLICY = "http://localhost:8194/"
    ARGOS_ALARM = "http://localhost:8195/"
    ARGOS_CHATBOT = "http://localhost:8198/"

# Api Information
class ModuleInfo:
    _map: Dict[str, ModuleObject] = {}

    @classmethod
    def set_map(cls, m: Dict[str, ModuleObject]) -> None:
        cls._map = m

    @classmethod
    def get(cls, code: str) -> Optional[ModuleObject]:
        return cls._map.get(code).getUrl()