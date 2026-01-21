import logging
import asyncio
import random
from typing import List, Dict, Any, Optional, Tuple
from playwright.async_api import Page, BrowserContext
from fake_useragent import UserAgent
from .browser_pool import get_browser_pool

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self):
        self.ua = UserAgent()
        self._page: Optional[Page] = None
        self._context: Optional[BrowserContext] = None

    async def _get_page(self) -> Tuple[Page, BrowserContext]:
        """
        Get a new page from the browser pool.
        
        Returns:
            Tuple of (Page, BrowserContext)
        """
        pool = await get_browser_pool()
        page, context = await pool.get_page()
        self._page = page
        self._context = context
        return page, context

    async def _safe_close(self):
        """Safely close page and context."""
        try:
            if self._page or self._context:
                pool = await get_browser_pool()
                await pool.close_page(self._page, self._context)
                self._page = None
                self._context = None
        except Exception as e:
            logger.debug(f"Error closing page/context: {e}")

    async def _random_delay(self, min_seconds=2, max_seconds=5):
        """Add random delay to avoid detection."""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    def normalize_job_data(self, raw_job: Dict[str, Any], source: str, country: str = "India") -> Dict[str, Any]:
        """
        Normalize job data to a consistent format.
        
        Args:
            raw_job: Raw job data from scraper
            source: Source name (e.g., "LinkedIn", "Naukri")
            country: Country name (e.g., "India", "UAE")
            
        Returns:
            Normalized job dictionary
        """
        # Generate a unique ID based on link and title
        job_id = abs(hash(raw_job.get("apply_link", "") + raw_job.get("title", ""))) % (10 ** 8)
        
        return {
            "id": job_id,
            "title": raw_job.get("title", "Unknown Role"),
            "company": raw_job.get("company", "Unknown Company"),
            "location": raw_job.get("location", country), # Default location to country if missing
            "country": country,
            "experience_min": raw_job.get("experience_min", 0),
            "experience_max": raw_job.get("experience_max", 0),
            "ctc_min": raw_job.get("ctc_min"),
            "ctc_max": raw_job.get("ctc_max"),
            "skills": raw_job.get("skills", []),
            "posted_at": raw_job.get("posted_at"),
            "apply_link": raw_job.get("apply_link", ""),
            "source": source,
            "logo_url": raw_job.get("logo_url"),
            "description": raw_job.get("description", "")
        }
