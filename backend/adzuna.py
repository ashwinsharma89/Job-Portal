import httpx
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AdzunaClient:
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/search"
        
    async def search_jobs(self, query: str, location: str = None, page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs using Adzuna API for India.
        Returns normalized job data.
        """
        if not self.app_id or not self.app_key:
            logger.warning("ADZUNA_APP_ID or ADZUNA_APP_KEY not set. Returning empty results.")
            return []
        
        jobs = []
        async with httpx.AsyncClient() as client:
            try:
                params = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "results_per_page": 50,
                    "what": query,
                    "content-type": "application/json"
                }
                
                if location:
                    params["where"] = location
                
                response = await client.get(
                    f"{self.base_url}/{page}",
                    params=params,
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()
                
                raw_jobs = data.get("results", [])
                jobs = [self._normalize_job(job) for job in raw_jobs]
                
            except httpx.HTTPError as e:
                logger.error(f"Adzuna API error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching jobs from Adzuna: {e}")
        
        return jobs
    
    def _normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Adzuna job data to our internal schema.
        """
        import hashlib
        
        # Generate unique ID from redirect_url
        job_id = abs(hash(raw_job.get("redirect_url", "") + raw_job.get("title", ""))) % (10 ** 8)
        
        # Parse salary
        salary_min = raw_job.get("salary_min")
        salary_max = raw_job.get("salary_max")
        
        # Parse location
        location_parts = []
        if raw_job.get("location", {}).get("area"):
            location_parts.append(raw_job["location"]["area"][0] if isinstance(raw_job["location"]["area"], list) else raw_job["location"]["area"])
        if raw_job.get("location", {}).get("display_name"):
            location_parts.append(raw_job["location"]["display_name"])
        location = ", ".join(filter(None, location_parts)) or "India"
        
        # Parse created date
        created_date = None
        if raw_job.get("created"):
            try:
                from dateutil import parser
                created_date = parser.parse(raw_job["created"])
            except:
                pass
        
        return {
            "id": job_id,
            "title": raw_job.get("title", "Unknown Role"),
            "company": raw_job.get("company", {}).get("display_name", "Unknown Company"),
            "location": location,
            "experience_min": 0,  # Adzuna doesn't provide experience directly
            "experience_max": 0,
            "ctc_min": salary_min,
            "ctc_max": salary_max,
            "skills": [],  # Would need to extract from description
            "posted_at": created_date,
            "apply_link": raw_job.get("redirect_url"),
            "source": "Adzuna",  # Mark source as Adzuna
            "logo_url": raw_job.get("company", {}).get("logo_url"),
            "description": raw_job.get("description", "")
        }
