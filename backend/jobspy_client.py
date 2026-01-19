import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from jobspy import scrape_jobs

logger = logging.getLogger(__name__)

class JobSpyClient:
    def __init__(self):
        # sites to scrape: linkedin, indeed, glassdoor, zip_recruiter
        self.sites = ["linkedin", "indeed", "glassdoor"]
        
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs using JobSpy (scrapes LinkedIn, Indeed, etc.).
        Note: JobSpy is synchronous/blocking, so we should run it carefully, 
        but for simplicity in this MVP we call it directly.
        In a prod app, run this in a thread pool executor.
        """
        jobs_list = []
        try:
            # JobSpy expects 'results_wanted' (count), not pages directly.
            # We'll fetch 10 results per call.
            # It also takes 'country_indeed' parameter.
            
            logger.info(f"JobSpy scraping for '{query}' in '{location}'...")
            
            # Scrape jobs
            jobs_df = scrape_jobs(
                site_name=self.sites,
                search_term=query,
                location=location,
                results_wanted=10,
                country_indeed='India',
                offset=(page - 1) * 10 
            )
            
            if jobs_df is not None and not jobs_df.empty:
                logger.info(f"JobSpy found {len(jobs_df)} jobs")
                # Convert DataFrame to list of dicts
                raw_jobs = jobs_df.to_dict('records')
                jobs_list = [self._normalize_job(job) for job in raw_jobs]
            else:
                logger.info("JobSpy returned no jobs")
                
        except Exception as e:
            logger.error(f"JobSpy error: {e}")
        
        return jobs_list
    
    def _normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize JobSpy job data to our internal schema.
        """
        import hashlib
        
        # JobSpy returns fields: id, site, job_url, title, company, location, date_posted, etc.
        
        # Generate unique ID
        job_url = raw_job.get("job_url") or ""
        job_title = raw_job.get("title") or ""
        job_id = abs(hash(job_url + job_title)) % (10 ** 8)
        
        # Parse salary if available (JobSpy might return interval/min/max)
        ctc_min = None
        ctc_max = None
        if raw_job.get("min_amount"):
            try:
                ctc_min = float(raw_job["min_amount"])
            except:
                pass
        if raw_job.get("max_amount"):
            try:
                ctc_max = float(raw_job["max_amount"])
            except:
                pass
                
        # Date
        posted_at = None
        if raw_job.get("date_posted"):
            # jobspy often returns date object or string
            d = raw_job["date_posted"]
            if isinstance(d, datetime):
                posted_at = d
            else:
                try:
                    from dateutil import parser
                    posted_at = parser.parse(str(d))
                except:
                    pass

        description = raw_job.get("description") or ""

        return {
            "id": job_id,
            "title": job_title,
            "company": raw_job.get("company") or "Unknown Company",
            "location": raw_job.get("location") or "Remote",
            "experience_min": 0,
            "experience_max": 0,
            "ctc_min": ctc_min,
            "ctc_max": ctc_max,
            "skills": [], 
            "posted_at": posted_at,
            "apply_link": job_url,
            "source": raw_job.get("site", "JobSpy").capitalize(), # e.g. "Linkedin", "Indeed"
            "logo_url": raw_job.get("company_url"), # JobSpy doesn't always give logo, sometime company url
            "description": description[:3000] # Limit description
        }
