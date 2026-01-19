import httpx
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RemotiveClient:
    def __init__(self):
        # Remotive API doesn't require authentication for basic access
        # But you can optionally use an API key for higher limits
        self.api_key = os.getenv("REMOTIVE_API_KEY", "")
        self.base_url = "https://remotive.com/api/remote-jobs"
        
    async def search_jobs(self, query: str = None, category: str = None, country: str = None) -> List[Dict[str, Any]]:
        """
        Search for remote jobs using Remotive API.
        Note: Remotive doesn't support traditional pagination or location filtering.
        It returns all active remote jobs, which we then filter.
        """
        # Remotive is primarily global/US. If searching for specific country like UAE,
        # it's better to skip to avoid pollution unless explicitly looking for Remote.
        if country and country.lower() in ["uae", "ae", "united arab emirates"]:
            return []

        jobs = []
        async with httpx.AsyncClient() as client:
            try:
                params = {}
                if category:
                    params["category"] = category
                
                # Add API key if available
                if self.api_key:
                    params["api_key"] = self.api_key
                
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()
                
                raw_jobs = data.get("jobs", [])
                
                # Filter by query if provided
                if query:
                    query_lower = query.lower()
                    raw_jobs = [
                        job for job in raw_jobs
                        if query_lower in job.get("title", "").lower() or
                           query_lower in job.get("description", "").lower() or
                           query_lower in job.get("company_name", "").lower()
                    ]
                
                # No limit to match other high-volume APIs
                # raw_jobs = raw_jobs[:20]
                
                jobs = [self._normalize_job(job) for job in raw_jobs]
                
            except httpx.HTTPError as e:
                logger.error(f"Remotive API error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching jobs from Remotive: {e}")
        
        return jobs
    
    def _normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Remotive job data to our internal schema.
        """
        # Generate unique ID from job URL
        job_id = abs(hash(raw_job.get("url", "") + str(raw_job.get("id", "")))) % (10 ** 8)
        
        # Parse salary (Remotive provides salary as a string like "$80k - $120k")
        salary_text = raw_job.get("salary", "")
        ctc_min = None
        ctc_max = None
        
        # Parse publication date
        posted_at = None
        if raw_job.get("publication_date"):
            try:
                from dateutil import parser
                posted_at = parser.parse(raw_job["publication_date"])
            except:
                pass
        
        # Extract tags as skills
        tags = raw_job.get("tags", [])
        
        return {
            "id": job_id,
            "title": raw_job.get("title", "Unknown Role"),
            "company": raw_job.get("company_name", "Unknown Company"),
            "location": "Remote",  # All Remotive jobs are remote
            "experience_min": 0,
            "experience_max": 0,
            "ctc_min": ctc_min,
            "ctc_max": ctc_max,
            "skills": tags[:5] if tags else [],  # Limit to 5 tags
            "posted_at": posted_at,
            "apply_link": raw_job.get("url"),
            "source": "Remotive",
            "logo_url": raw_job.get("company_logo"),
            "description": raw_job.get("description", "")[:1000]  # Limit description length
        }
