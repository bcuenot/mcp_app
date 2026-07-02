from fastapi import APIRouter, File, Form, UploadFile, Header, Depends, HTTPException
from pydantic import BaseModel, Field
from dependencies.auth import extract_bearer_token

from sqlalchemy.orm import Session
from database.database import get_db
from services.agent_service import AgentService, AgentServiceError
from services.token_service import TokenService, TokenExchangeError
from services.messages_service import MessagesService
from services.conversations_service import ConversationService
from services.auth_service import AuthService, AuthenticationError, AuthenticationExpiredError, AuthenticationServerUnavailableError
from services.files_service import FilesService, FilesError
from models.message import MessageRole
from models.message import Message
from models.conversation import Conversation

router = APIRouter()
agent_service = AgentService()
auth_service = AuthService()
token_service = TokenService()
message_service = MessagesService()
conversation_service = ConversationService()
files_service = FilesService()

class ChatResponse(BaseModel):
    message: str
    conversation_id : str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message : str = Form(...), 
    conversation_id : str | None = Form(default=None),
    files : list[UploadFile] | None = Form(default=None),
    authorization: str | None = Header(default=None), 
    database: Session = Depends(get_db)):

    user_access_token: str = extract_bearer_token(authorization)
    if files:
        for file in files:
            print(file)

    try:
        user_id: str = auth_service.get_user_id(access_token=user_access_token)
        if conversation_id is None:
            conversation : Conversation = conversation_service.create_conversation(
                database=database,
                user_id=user_id,
                title=message[:20],
            )
            conversation_id = conversation.id

        mcp_access_token: str = await token_service.exchange_token_for_mcp(user_access_token)
        history_messages : list[Message] = message_service.get_messages_by_conversation_id(database=database, conversation_id=conversation_id, user_id=user_id)
        files_content : str | None = await files_service.build_files_context(files=files)
        answer: str = await agent_service.ask(message=message, files_content=files_content, history_messages=history_messages, mcp_access_token=mcp_access_token)

        user_message = message_service.create_message(
            database=database,
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=message,
        )

        if user_message is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation introuvable.",
            )

        assistant_message = message_service.create_message(
            database=database,
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=answer,
        )

        if assistant_message is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation introuvable.",
            )

        return ChatResponse(message=answer, conversation_id=conversation_id)

    except AuthenticationExpiredError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    except AuthenticationError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    except AuthenticationServerUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    except TokenExchangeError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    except AgentServiceError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur inattendue : {type(error).__name__}: {error}",
        ) from error
