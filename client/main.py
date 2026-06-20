from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.database import Base, engine
from models.conversation import Conversation
from models.message import Message
from routers.chat_router import router as chat_router
from routers.conversations import router as conversations_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="MCP Client Backend", lifespan=lifespan)

app.include_router(chat_router)
app.include_router(conversations_router)

@app.get("/health")
async def health():
    return {"status": "ok"}