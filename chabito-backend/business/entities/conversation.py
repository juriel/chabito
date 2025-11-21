from typing import Optional
from pydantic import BaseModel

class ChatContact(BaseModel):
    uuid: str
    name: str
    avatar_url: Optional[str] = None