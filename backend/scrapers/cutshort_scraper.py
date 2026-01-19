import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class CutshortScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on Cutshort.io.
        URL: https://cutshort.io/search-jobs?free_text={query} {location}
        """
        jobs = []
        try:
            # Cutshort uses search params
            search_text = f"{query} {location}"
            query_encoded = urllib.parse.quote(search_text)
            
            url = f"https://cutshort.io/search-jobs?free_text={query_encoded}"
            
            logger.info(f"Scraping Cutshort: {url}")
            
            page_obj, context = await self._get_page()
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(2) # Extra buffer for heavy SPA
            
            # Cutshort often uses generic classes or dynamic selectors
            # Based on discovery, we look for h3 (title) and company info
            cards = await page_obj.query_selector_all("div[class*='JobCard'], .job-card")
            
            if not cards:
                # Fallback to looking for elements with 'Apply' button
                cards = await page_obj.query_selector_all("div:has(h3)")

            for card in cards:
                try:
                    title_el = await card.query_selector("h3")
                    company_el = await card.query_selector("div[class*='company-info'], .company-name")
                    link_el = await card.query_selector("a[href*='/jobs/']")
                    
                    if not title_el: continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://cutshort.io{link}"
                    
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location, # Cutshort cards don't always show location clearly in list
                        "apply_link": link,
                        "description": f"View details on Cutshort: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Cutshort"))
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Cutshort scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
