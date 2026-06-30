from sqlalchemy import select
from sqlalchemy.orm import Session
from models.conversation import Conversation


class ConversationRepository:

    def get_conversation_summaries_by_user_id(self, database : Session, user_id : str) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )

        conversations : list[Conversation] = database.scalars(statement).all()

        return conversations

    def create_conversation(self, database : Session, user_id : str, title : str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        database.add(conversation)
        database.commit()
        database.refresh(conversation)

        return conversation 
    
    def update_conversation_title(self, database : Session, conversation_id : str, user_id : str, new_conversation_title : str) -> Conversation | None:
        statement = (
            select(Conversation)
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        conversation : Conversation | None = database.scalars(statement).first()

        if conversation is None :
            return None
        
        conversation.title = new_conversation_title

        database.add(conversation)
        database.commit()
        database.refresh(conversation)

        return conversation