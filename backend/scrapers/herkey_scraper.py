import logging
import asyncio
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class HerKeyScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from HerKey.
        URL pattern: https://www.herkey.com/search?keyword={query}&moduleName=jobs
        """
        jobs = []
        try:
            # HerKey uses query parameters
            url = f"https://www.herkey.com/search?keyword={urllib.parse.quote(query)}&moduleName=jobs"
            
            if page > 1:
                url += f"&page={page}"
            
            logger.info(f"Scraping HerKey: {url}")
            
            page_obj, context = await self._get_page()
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self._random_delay(3, 5)
            
            # HerKey uses various selectors
            cards = await page_obj.query_selector_all("div.job-card, div[class*='job-listing'], article, div[class*='card']")
            
            # Fallback
            if not cards or len(cards) == 0:
                cards = await page_obj.query_selector_all("a[href*='/job/'], a[href*='/jobs/']")
            
            logger.info(f"Found {len(cards)} job cards on HerKey")
            
            for card in cards:
                try:
                    text = await card.inner_text()
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    
                    if not lines or len(lines) < 1:
                        continue
                    
                    # Parse title and company
                    title = lines[0]
                    company = lines[1] if len(lines) > 1 else "Various"
                    
                    # Look for location
                    loc_text = location
                    for line in lines:
                        if any(city in line for city in ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Remote"]):
                            loc_text = line
                            break
                    
                    # Get link
                    if card.tag_name == "a":
                        link = await card.get_attribute("href")
                    else:
                        link_el = await card.query_selector("a")
                        link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = "https://www.herkey.com" + link
                    
                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": loc_text,
                        "apply_link": link,
                        "description": text[:500]
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "HerKey"))
                    
                except Exception as e:
                    logger.debug(f"Error parsing HerKey job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"HerKey scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
