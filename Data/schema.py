from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class ChatObject(BaseModel):
    empno: str
    sender: str
    message: str
    sent_at: Optional[datetime] = None
    intent: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)