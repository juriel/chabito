from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class MessageDTO(BaseModel):
    message: str
    source: str
    destination: str


class ChatRequestDTO(BaseModel):
    message: str
    user_id: str
    sender_nickname: Optional[str] = None
    sender_jid: Optional[str] = None
    mime_type: Optional[str] = None
    file_base64: Optional[str] = None 
    def __str__(self):
        return (
            f"ChatRequestDTO(message={self.message}, user_id={self.user_id}, "
            f"sender_nickname={self.sender_nickname}, sender_jid={self.sender_jid}, "
            f"mime_type={self.mime_type}, file_base64={self.file_base64})"
        )


class ChatResponseDTO(BaseModel):
    response_message: str
    mime_type: Optional[str] = None
    file_base64: Optional[str] = None
    
