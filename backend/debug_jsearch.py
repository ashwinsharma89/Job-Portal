import asyncio
import logging
from jsearch import JSearchClient
from dotenv import load_dotenv
import os

# Load env from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JSearchDebug")

async def test_jsearch():
    client = JSearchClient()
    print(f"🔑 API Key Present: {bool(client.api_key)}")
    print(f"🌍 Host: {client.host}")
    
    print("🚀 Starting JSearch Test...")
    try:
        jobs = await client.search_jobs("Data Scientist in Delhi NCR", 1, 1, "India")
        print(f"📊 Found {len(jobs)} jobs.")
        
        if len(jobs) > 0:
            print(f"✅ Sample 1: {jobs[0]['title']} at {jobs[0]['company']}")
            print(f"🔗 Link: {jobs[0]['apply_link']}")
        else:
            print("❌ No jobs found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_jsearch())
