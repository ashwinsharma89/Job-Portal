import asyncio
import logging
from typing import List, Dict, Any
from jsearch import JSearchClient
from adzuna import AdzunaClient
from remotive import RemotiveClient
from scrapers.naukri_scraper import NaukriScraper
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.instahyre_scraper import InstahyreScraper
from scrapers.iimjobs_scraper import IimjobsScraper
from scrapers.hirist_scraper import HiristScraper
from scrapers.herkey_scraper import HerKeyScraper
from scrapers.cutshort_scraper import CutshortScraper
from scrapers.freshersworld_scraper import FreshersworldScraper
from scrapers.apna_scraper import ApnaScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.foundit_scraper import FounditScraper
from scrapers.ziprecruiter_scraper import ZipRecruiterScraper
from scrapers.ziprecruiter_scraper import ZipRecruiterScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.naukrigulf_scraper import NaukriGulfScraper
from scrapers.bayt_scraper import BaytScraper
from scrapers.gulftalent_scraper import GulfTalentScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    def __init__(self):
        # Initialize all clients
        self.jsearch_client = JSearchClient()
        self.adzuna_client = AdzunaClient()
        self.remotive_client = RemotiveClient()
        self.scrapers = {
            "Naukri": NaukriScraper(),
            "LinkedIn": LinkedInScraper(),
            "Instahyre": InstahyreScraper(),
            "Iimjobs": IimjobsScraper(),
            "Hirist": HiristScraper(),
            "HerKey": HerKeyScraper(),
            "Cutshort": CutshortScraper(),
            "Freshersworld": FreshersworldScraper(),
            "Apna": ApnaScraper(),
            "Indeed": IndeedScraper(),
            "Foundit": FounditScraper(),
            "ZipRecruiter": ZipRecruiterScraper(),
            "Glassdoor": GlassdoorScraper(),
            "NaukriGulf": NaukriGulfScraper(),
            "Bayt": BaytScraper(),
            "GulfTalent": GulfTalentScraper()
        }

    async def execute_search(self, query: str, location: str = "India", page: int = 1, country: str = "India") -> List[Dict[str, Any]]:
        """
        Execute all configured scrapers concurrently with timeouts.
        """
        search_term = query
        if location:
            search_term_with_loc = f"{query} in {location}"
        else:
            search_term_with_loc = query
            # Default location logic to prevent NoneType errors in scrapers
            if country.lower() in ["uae", "ae", "united arab emirates"]:
                location = "Dubai"
            else:
                location = "India"

        logger.info(f"ScraperManager: Starting concurrent search for '{search_term}' in {country}")
        
        tasks = []

        # 1. API Clients (Fast)
        # 1. API Clients (Fast)
        tasks.append(self._run_wrapper(
            self.jsearch_client.search_jobs(search_term_with_loc, page=page, num_pages=2, country=country), 
            "JSearch", 10
        ))
        
        # Remotive (Global/Remote) - Keep it for both but it's international
        tasks.append(self._run_wrapper(
            self.remotive_client.search_jobs(search_term, country=country), 
            "Remotive", 10
        ))
        
        # 2. Adzuna (Reliable but rate-limited)
        # Verify if country is supported by Adzuna (India only in current config)
        if country.lower() not in ["uae", "ae", "united arab emirates"]:
            for i in range(2):
                tasks.append(self._run_wrapper(
                    self.adzuna_client.search_jobs(query, location, page + i), 
                    f"Adzuna-{i+1}", 20
                ))

        # 3. Scrapers (Playwright)
        # Priority Scrapers (Higher timeout)
        priority_scrapers = ["Hirist", "Foundit", "Iimjobs", "Naukri", "Indeed"]
        
        for name, scraper in self.scrapers.items():
            # Country-Specific Logic
            is_uae = country.lower() in ["uae", "ae", "united arab emirates"]
            is_india = not is_uae # Default to India
            
            # Skip India-specific sites if UAE
            if is_uae and name in ["Hirist", "Instahyre", "Freshersworld", "Cutshort", "Naukri", "Iimjobs"]:
                continue
                
            # Skip UAE-specific sites if India
            if is_india and name in ["NaukriGulf", "Bayt", "GulfTalent"]:
                continue

            timeout = 45 if name in priority_scrapers else 25
            
            # Safe call handling for country argument
            if name in ["Indeed", "NaukriGulf", "Bayt", "GulfTalent"]:
                 tasks.append(self._run_wrapper(
                    scraper.search_jobs(query, location, page, country=country),
                    name, timeout
                ))
            else:
                 tasks.append(self._run_wrapper(
                    scraper.search_jobs(query, location, page),
                    name, timeout
                ))

        # Execute all
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_jobs = []
        for res in results:
            if isinstance(res, list):
                all_jobs.extend(res)
        
        logger.info(f"ScraperManager: Total jobs collected: {len(all_jobs)}")
        return all_jobs

    async def _run_wrapper(self, coro, name: str, timeout: int) -> List[Dict[str, Any]]:
        """
        Helper to run a scraper coroutine with timeout and error handling.
        """
        try:
            start_time = asyncio.get_event_loop().time()
            result = await asyncio.wait_for(coro, timeout=timeout)
            elapsed = asyncio.get_event_loop().time() - start_time
            
            count = len(result) if isinstance(result, list) else 0
            logger.info(f"✅ {name} finished in {elapsed:.1f}s: {count} jobs")
            return result if isinstance(result, list) else []
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ {name} timed out after {timeout}s")
            return []
        except Exception as e:
            logger.error(f"❌ {name} failed: {str(e)}")
            return []
