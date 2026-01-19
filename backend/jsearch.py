import httpx
import os
import logging
from typing import List, Dict, Any, Optional
from dateutil import parser

logger = logging.getLogger(__name__)

class JSearchClient:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
        self.base_url = f"https://{self.host}/search"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host,
        }

    async def search_jobs(self, query: str, page: int = 1, num_pages: int = 3, country: str = "India") -> List[Dict[str, Any]]:
        """
        Search for jobs using JSearch API.
        Fetches 3 pages by default (30 jobs total) for better pagination.
        """
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY not set. Returning empty results.")
            return []
            
        # Map full country names to ISO codes
        country_map = {
            "india": "IN",
            "uae": "AE",
            "united arab emirates": "AE",
            "dubai": "AE"
        }
        country_code = country_map.get(country.lower(), "IN")

        jobs = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    headers=self.headers,
                    params={
                        "query": query,
                        "page": str(page),
                        "num_pages": str(num_pages) if num_pages else "4",
                        "country": country_code, 
                    },
                    timeout=15.0  # Increased timeout for multiple pages
                )
                response.raise_for_status()
                data = response.json()
                
                raw_jobs = data.get("data", [])
                jobs = [self._normalize_job(job, country) for job in raw_jobs]
                
            except httpx.HTTPError as e:
                logger.error(f"JSearch API error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching jobs: {e}")
                
        return jobs

    def _normalize_job(self, raw_job: Dict[str, Any], country: str = "India") -> Dict[str, Any]:
        """
        Normalize JSearch job data to our internal schema.
        """
        # Generate a unique ID from the apply link
        import hashlib
        job_id = abs(hash(raw_job.get("job_apply_link", "") + raw_job.get("job_title", ""))) % (10 ** 8)
        
        return {
            "id": job_id,
            "title": raw_job.get("job_title", "Unknown Role"),
            "company": raw_job.get("employer_name", "Unknown Company"),
            "location": f"{raw_job.get('job_city')}, {raw_job.get('job_country')}" if raw_job.get('job_city') else country,
            "country": country,
            "experience_min": 0, # Placeholder, hard to extract reliably without NLP
            "experience_max": 0, # Placeholder
            "ctc_min": raw_job.get("job_min_salary"),
            "ctc_max": raw_job.get("job_max_salary"),
            "skills": [], # Placeholder, usually needs keyword extraction from description
            "posted_at": parser.parse(raw_job.get("job_posted_at_datetime_utc")) if raw_job.get("job_posted_at_datetime_utc") else None,
            "apply_link": raw_job.get("job_apply_link"),
            "source": raw_job.get("job_publisher", "JSearch"),
            "logo_url": raw_job.get("employer_logo"),
            "description": raw_job.get("job_description", "") # Store full description or at least enough for searching
        }
