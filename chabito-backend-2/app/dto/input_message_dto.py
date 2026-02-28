from typing import Optional

from pydantic import BaseModel


class InputMessageDTO(BaseModel):
    message: str
    user_id: str
    sender_nickname: Optional[str] = None
    sender_jid: Optional[str] = None
    mime_type: Optional[str] = None
    file_base64: Optional[str] = None

