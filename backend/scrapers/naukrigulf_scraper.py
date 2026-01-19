import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class NaukriGulfScraper(BaseScraper):
    """
    Scraper for NaukriGulf (UAE/Middle East).
    """
    async def search_jobs(self, query: str, location: str = "Dubai", page: int = 1, country: str = "UAE", **kwargs) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # URL Structure: https://www.naukrigulf.com/[query]-jobs-in-[location]
            # Or search params: https://www.naukrigulf.com/search-jobs?keywords=python&location=dubai
            
            q_enc = urllib.parse.quote(query)
            l_enc = urllib.parse.quote(location)
            
            # Using the search-jobs endpoint approach
            url = f"https://www.naukrigulf.com/search-jobs?keywords={q_enc}&location={l_enc}&currPage={page}"
            
            logger.info(f"Scraping NaukriGulf: {url}")
            
            page_obj, context = await self._get_page()
            
            # NaukriGulf might have bot protection, but usually less strict than Naukri India
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Wait for list logic
            try:
                await page_obj.wait_for_selector(".srp-tuple-layout, .job-tuple", timeout=15000)
            except:
                logger.warning("No NaukriGulf jobs found or timeout.")
                return []
                
            # Select cards
            cards = await page_obj.query_selector_all(".srp-tuple-layout, .job-tuple")
            
            for card in cards:
                try:
                    title_el = await card.query_selector(".designation-title, .job-title")
                    company_el = await card.query_selector(".org-name, .company-name")
                    location_el = await card.query_selector(".loc-name, .location-name")
                    link_el = await card.query_selector("a.designation-title, a.job-title")
                    
                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.naukrigulf.com{link}"
                        
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on NaukriGulf: {link}",
                        "source": "NaukriGulf"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "NaukriGulf", country))
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"NaukriGulf scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
