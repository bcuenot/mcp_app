import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.environ["DATABASE_URL"]


class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL,pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()