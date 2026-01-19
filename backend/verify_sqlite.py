import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

DATABASE_URL = "sqlite+aiosqlite:///./jobplatform.db"

async def main():
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection successful! Result: {result.scalar()}")
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
