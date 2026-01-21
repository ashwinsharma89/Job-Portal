import asyncio
from sqlalchemy import select
from database import AsyncSessionLocal
from models import Job
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def inspect_jobs():
    async with AsyncSessionLocal() as session:
        # Fetch jobs with 'Data Scientist' in title
        result = await session.execute(select(Job).where(Job.title.ilike("%Data Scientist%")).limit(10))
        jobs = result.scalars().all()
        
        print("\n--- Inspecting Jobs ---")
        for job in jobs:
            print(f"ID: {job.id}")
            print(f"Title: {job.title}")
            print(f"Exp Raw: {job.experience_min} - {job.experience_max}")
            print("-" * 20)
            
        # Check jobs with 0 experience
        result = await session.execute(select(Job).where(Job.experience_min == 0).limit(5))
        zero_jobs = result.scalars().all()
        print(f"\nSample Jobs with 0 Exp: {len(zero_jobs)}")
        for job in zero_jobs:
            print(f"ID: {job.id} | Exp: {job.experience_min}-{job.experience_max}")

if __name__ == "__main__":
    asyncio.run(inspect_jobs())
