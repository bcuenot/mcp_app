from sqlalchemy.orm import Session

from models.conversation import Conversation
from repositories.conversations_repository import ConversationRepository

class ConversationService:
    def __init__(self, conversation_repository : ConversationRepository | None = None):
        self.repository = conversation_repository or ConversationRepository()

    def get_conversation_summaries_by_user_id(self, database : Session, user_id : str) -> list[Conversation]:
        conversations : list[Conversation] = self.repository.get_conversation_summaries_by_user_id(database=database, user_id=user_id)

        return conversations
    
    def create_conversation(self, database : Session, user_id : str, title : str) -> Conversation:
        conversation : Conversation = self.repository.create_conversation(database=database, user_id=user_id, title=title)

        return conversation
    
    def update_conversation_title(self, database : Session, conversation_id : str, user_id : str, new_conversation_title : str) -> Conversation | None:
        conversation : Conversation = self.repository.update_conversation_title(database=database, conversation_id=conversation_id, user_id=user_id, new_conversation_title=new_conversation_title)

        return conversation
    
        

    