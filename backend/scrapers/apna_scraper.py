import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class ApnaScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on Apna.co.
        URL: https://apna.co/jobs?q={query}&location={location}
        """
        jobs = []
        try:
            query_encoded = urllib.parse.quote(query)
            loc_encoded = urllib.parse.quote(location)
            url = f"https://apna.co/jobs?q={query_encoded}&location={loc_encoded}"
            
            logger.info(f"Scraping Apna: {url}")
            
            page_obj, context = await self._get_page()
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for cards
            await page_obj.wait_for_selector("a[href^='/job/']", timeout=10000)
            
            cards = await page_obj.query_selector_all("a[href^='/job/']")
            
            for card in cards:
                try:
                    title_el = await card.query_selector("h2")
                    company_el = await card.query_selector("div[class*='JobCompany']")
                    location_el = await card.query_selector("p[class*='leading']")
                    
                    if not title_el: continue
                    
                    title = await title_el.inner_text()
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await card.get_attribute("href")
                    
                    if link and not link.startswith("http"):
                        link = f"https://apna.co{link}"
                        
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on Apna: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Apna"))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Apna scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
