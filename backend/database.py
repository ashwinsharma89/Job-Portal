from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback/Placeholder for when env vars aren't set yet to prevent import errors during init
    DATABASE_URL = "sqlite+aiosqlite:///./jobplatform.db"

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Optimize SQLite for Concurrency (WAL Mode)
from sqlalchemy import event
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
