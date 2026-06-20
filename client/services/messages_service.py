from sqlalchemy.orm import Session

from models.message import Message
from repositories.messages_repository import MessageRepository
from models.message import MessageRole

class MessagesService:
    def __init__(self, message_repository : MessageRepository | None = None):
        self.repository = message_repository or MessageRepository()

    def get_messages_by_conversation_id(self, database : Session, conversation_id : str, user_id : str) -> list[Message]:
        messages : list[Message] = self.repository.get_messages_summaries_by_user_id(database=database, conversation_id=conversation_id, user_id=user_id)

        return messages
    
    def create_message(self, database : Session, conversation_id : str, user_id : str, role : MessageRole, content : str) -> Message | None:
        message : Message = self.repository.create_message(database=database, conversation_id=conversation_id, user_id=user_id, role=role, content=content)

        return message
        

    