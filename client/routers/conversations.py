from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from database.database import get_db
from models.conversation import Conversation
from models.message import Message
from dependencies.auth import extract_bearer_token
from services.conversations_service import ConversationService
from services.messages_service import MessagesService
from services.auth_service import AuthService, AuthenticationError, AuthenticationExpiredError, AuthenticationServerUnavailableError

router = APIRouter()
auth_service = AuthService()
conversation_service = ConversationService()
message_service = MessagesService()

class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str

class MessageSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role : str
    content : str

class UpdateConversationTitleRequest(BaseModel):
    new_conversation_title: str = Field(min_length=1, max_length=40)

class UpdateConversationTitleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id : str
    title : str

@router.get("/conversations", response_model = list[ConversationSummary])
def conversations(authorization: str | None = Header(default=None), database: Session = Depends(get_db)):
    access_token : str = extract_bearer_token(authorization=authorization)
    try:
        user_id : str = auth_service.get_user_id(access_token=access_token)
        conversations : list[Conversation] = conversation_service.get_conversation_summaries_by_user_id(database=database, user_id=user_id)

        return conversations

    except AuthenticationExpiredError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationServerUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

@router.get("/conversations/{conversation_id}/messages", response_model= list[MessageSummary])
def get_messages_by_conversation_id(conversation_id : str, authorization : str | None = Header(default=None), database: Session = Depends(get_db)):
    access_token : str = extract_bearer_token(authorization=authorization)
    try:
        user_id : str = auth_service.get_user_id(access_token=access_token)
        messages : list[Message] = message_service.get_messages_by_conversation_id(database=database, conversation_id=conversation_id, user_id=user_id)

        return messages
    
    except AuthenticationExpiredError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationServerUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    

@router.patch("/conversations/{conversation_id}", response_model= UpdateConversationTitleResponse)
def update_conversation_id(conversation_id : str, payload: UpdateConversationTitleRequest, authorization : str | None = Header(default=None), database: Session = Depends(get_db)):
    access_token : str = extract_bearer_token(authorization=authorization)
    try:
        user_id : str = auth_service.get_user_id(access_token=access_token)
        conversation : Conversation = conversation_service.update_conversation_title(
            database=database, 
            conversation_id=conversation_id, 
            user_id=user_id, 
            new_conversation_title=payload.new_conversation_title
        )

        return conversation
    
    except AuthenticationExpiredError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        ) from error

    except AuthenticationServerUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error