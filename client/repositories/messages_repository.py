from sqlalchemy import select
from sqlalchemy.orm import Session
from models.message import Message
from models.conversation import Conversation
from models.message import MessageRole
from datetime import datetime, timezone


class MessageRepository:

    def get_messages_by_conversation_id(self, database : Session, conversation_id : str, user_id : str) -> list[Message]:
        statement = (
            select(Message)
            .join(Conversation)
            .where(
                Message.conversation_id == conversation_id,
                Conversation.user_id == user_id
            )
            .order_by(Message.created_at.asc())
        )

        messages : list[Message] = database.scalars(statement).all()

        return messages
    
    def create_message(self, database : Session, conversation_id : str, user_id : str, role : MessageRole, content : str) -> Message | None: 

        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        conversation = database.scalar(statement)
        if conversation is None:
            return None
        
        message = Message(conversation_id = conversation_id, role = role.value, content = content)
        conversation.updated_at = datetime.now(timezone.utc)
        database.add(message)
        database.commit()
        database.refresh(message)

        return message

