import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class GulfTalentScraper(BaseScraper):
    """
    Scraper for GulfTalent (UAE/Middle East).
    """
    async def search_jobs(self, query: str, location: str = "UAE", page: int = 1, **kwargs) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # GulfTalent Search URL
            # https://www.gulftalent.com/uae/jobs/search?keywords=python
            
            q_enc = urllib.parse.quote(query)
            
            # Location handling: GulfTalent is country based often in URL
            # If location is Dubai, we can search in UAE context
            url = f"https://www.gulftalent.com/uae/jobs/search?keywords={q_enc}&start={(page-1)*20}"
            
            logger.info(f"Scraping GulfTalent: {url}")
            
            page_obj, context = await self._get_page()
            
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for list (GulfTalent uses table or list)
            try:
                await page_obj.wait_for_selector(".job-results-list, tr.job-item, .job-list-item", timeout=15000)
            except:
                logger.warning("No GulfTalent jobs found or timeout.")
                return []
            
            # GulfTalent often uses a table row structure or list items
            # Selectors might need adjustment based on live site changes.
            # Common structure: class="job-item"
            cards = await page_obj.query_selector_all("tr.clickable-row, .job-list-item")
            
            for card in cards:
                try:
                    title_el = await card.query_selector(".job-title a, a[href*='/jobs/']")
                    company_el = await card.query_selector(".company-name")
                    location_el = await card.query_selector(".job-location")
                    link_el = title_el # Usually the title <a> has the link
                    
                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.gulftalent.com{link}"
                    
                    title = title.strip()
                    company = company.strip()
                    
                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on GulfTalent: {link}",
                        "source": "GulfTalent"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "GulfTalent"))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"GulfTalent scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
