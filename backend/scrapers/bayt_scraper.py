import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class BaytScraper(BaseScraper):
    """
    Scraper for Bayt.com (Middle East).
    """
    async def search_jobs(self, query: str, location: str = "Dubai", page: int = 1, country: str = "UAE", **kwargs) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # URL Structure: https://www.bayt.com/en/uae/jobs/q-{query}-l-{location}/
            # The search URL pattern is specific.
            
            # Simple Param based Search URL
            q_enc = urllib.parse.quote(query.replace(" ", "-"))
            l_enc = urllib.parse.quote(location.lower().replace(" ", "-"))
            
            # Page param is usually ?page=X
            url = f"https://www.bayt.com/en/uae/jobs/{q_enc}-jobs-in-{l_enc}/?page={page}"
            
            logger.info(f"Scraping Bayt: {url}")
            
            page_obj, context = await self._get_page()
            
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for list
            # Selector Update based on Browser Inspection (Jan 2026)
            try:
                # Wait for job list
                await page_obj.wait_for_selector("li[data-js-job]", timeout=15000)
            except:
                logger.warning("No Bayt jobs found or timeout.")
                return []
            
            # Select all job cards
            cards = await page_obj.query_selector_all("li[data-js-job]")
            
            for card in cards:
                try:
                    # Title
                    title_el = await card.query_selector("h2 a[data-js-aid='jobID']")
                    # Company (b for confidential, a.t-bold for others)
                    company_el = await card.query_selector("b, .t-bold")
                    # Location
                    location_el = await card.query_selector(".t-mute")
                    
                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await title_el.get_attribute("href") if title_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.bayt.com{link}"
                    
                    # Clean up strings
                    title = title.replace("\n", "").strip()
                    company = company.replace("\n", "").strip()
                    
                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on Bayt: {link}",
                        "source": "Bayt"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Bayt", country))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Bayt scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
