import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class FreshersworldScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on Freshersworld.
        URL Pattern: https://www.freshersworld.com/jobs/jobsearch/{query}-jobs
        """
        jobs = []
        try:
            query_slug = query.lower().replace(" ", "-")
            url = f"https://www.freshersworld.com/jobs/jobsearch/{query_slug}-jobs"
            
            logger.info(f"Scraping Freshersworld: {url}")
            
            page_obj, context = await self._get_page()
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for containers
            await page_obj.wait_for_selector(".job-container", timeout=10000)
            
            cards = await page_obj.query_selector_all(".job-container")
            
            for card in cards:
                try:
                    title_el = await card.query_selector("span.wrap-title.seo_title")
                    company_el = await card.query_selector(".bold_font") # Often location or company
                    
                    if not title_el: continue
                    
                    title = await title_el.inner_text()
                    
                    # Freshersworld structure: company is often a text node or sibling
                    # Let's try to extract from the card innerText if direct selector fails
                    card_text = await card.inner_text()
                    lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                    
                    company = "Unknown Company"
                    if len(lines) > 1:
                        company = lines[1] # Usually second line
                        
                    loc = location
                    if "Location" in card_text:
                        # Simple extraction
                        for line in lines:
                            if "Location" in line or "," in line:
                                loc = line.replace("Location:", "").strip()
                                break

                    link_el = await card.query_selector("a")
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.freshersworld.com{link}"
                        
                    raw_job = {
                        "title": title.strip(),
                        "company": company,
                        "location": loc,
                        "apply_link": link,
                        "description": f"View details on Freshersworld: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Freshersworld"))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Freshersworld scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
