from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# 채팅 요청/응답 오브젝트
class ChatObject(BaseModel):
    empno: str
    sender: str
    message: str
    sent_at: Optional[datetime] = None
    intent: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# 프로젝트 초기 로딩 시 API 정보 오브젝트
@dataclass
class ModuleObject:
    product_code: str
    product_url_http: str
    product_port: str

    def getUrl(self):
        # Ex) return "http://127.0.0.1:8190"
        return f"{self.product_url_http}:{self.product_port}"
