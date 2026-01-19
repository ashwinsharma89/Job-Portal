import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")
    print(f"Testing connection to: {url.split('@')[-1]}") # Don't print credentials
    try:
        conn = await asyncpg.connect(url, ssl='require')
        print("Successfully connected!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
