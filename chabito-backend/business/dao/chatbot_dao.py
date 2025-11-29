from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from business.common.dao import GenericDAO
from business.entities.chat import ChatContact, ChatConversation, ChatMessage


class ChatContactDAO(GenericDAO[ChatContact]):
    def __init__(self, session: Session):
        super().__init__(session, ChatContact)

    def find_by_phone_number(self, phone_number: str) -> Optional[ChatContact]:
        return self.findBy(phone_number=phone_number)


class ChatConversationDAO(GenericDAO[ChatConversation]):
    def __init__(self, session: Session):
        super().__init__(session, ChatConversation)

    def find_by_contact(self, chat_contact: UUID) -> List[ChatConversation]:
        return self.session.query(self.model).filter_by(chat_contact=chat_contact).all()

    def find_active_by_contact(self, chat_contact: UUID) -> Optional[ChatConversation]:
        return self.session.query(self.model).filter_by(
            chat_contact=chat_contact,
            status='active'
        ).first()

    def find_by_status(self, status: str) -> List[ChatConversation]:
        return self.session.query(self.model).filter_by(status=status).all()

    def update_last_message_at(self, conversation_id: UUID) -> Optional[ChatConversation]:
        return self.update(conversation_id, last_message_at=datetime.utcnow())


class ChatMessageDAO(GenericDAO[ChatMessage]):
    def __init__(self, session: Session):
        super().__init__(session, ChatMessage)

    def find_by_conversation(self, chat_conversation: UUID) -> List[ChatMessage]:
        return self.session.query(self.model).filter_by(
            chat_conversation=chat_conversation
        ).order_by(self.model.created_at).all()

    def find_by_conversation_and_type(self, chat_conversation: UUID, message_type: str) -> List[ChatMessage]:
        return self.session.query(self.model).filter_by(
            chat_conversation=chat_conversation,
            type=message_type
        ).order_by(self.model.created_at).all()

    def find_last_messages(self, chat_conversation: UUID, limit: int = 10) -> List[ChatMessage]:
        return self.session.query(self.model).filter_by(
            chat_conversation=chat_conversation
        ).order_by(self.model.created_at.desc()).limit(limit).all()

    def find_multimedia_messages(self, chat_conversation: UUID) -> List[ChatMessage]:
        return self.session.query(self.model).filter(
            self.model.chat_conversation == chat_conversation,
            self.model.mime_type.isnot(None)
        ).order_by(self.model.created_at).all()