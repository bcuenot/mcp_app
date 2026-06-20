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