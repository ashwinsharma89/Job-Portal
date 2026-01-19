import asyncio
import logging
from database import AsyncSessionLocal
from models import Job
from sqlalchemy import select
from managers.vector_manager import VectorManager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def backfill_vectors():
    logger.info("Starting Vector Backfill...")
    
    # 1. Initialize Vector Manager
    vm = VectorManager()
    
    # 2. Fetch all jobs from SQLite
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job))
        jobs = result.scalars().all()
        
        logger.info(f"Fetched {len(jobs)} jobs from SQLite")
        
        if not jobs:
            logger.warning("No jobs found in DB to index.")
            return

        # 3. Convert to Dict format for VectorManager
        job_dicts = []
        for job in jobs:
            # Safe handling of nulls
            skills = job.skills if isinstance(job.skills, list) else (job.skills.split(",") if job.skills else [])
            
            job_dicts.append({
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "description": job.description or "",
                "skills": skills,
                "location": job.location or "",
                "source": job.source or "unknown",
                "experience_min": job.experience_min or 0,
                "ctc_min": job.ctc_min or 0
            })
            
        # 4. Upsert (Index)
        logger.info("Indexing jobs to ChromaDB...")
        vm.upsert_jobs(job_dicts)
        
    logger.info("✅ Vector Backfill Complete!")

if __name__ == "__main__":
    asyncio.run(backfill_vectors())
