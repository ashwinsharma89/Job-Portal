import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    """
    Experimental Indeed Scraper.
    Note: Indeed has strong bot detection. This implementation uses best-effort stealth.
    """
    async def search_jobs(self, query: str, location: str = "India", page: int = 1, country: str = "India") -> List[Dict[str, Any]]:
        jobs = []
        try:
            query_encoded = urllib.parse.quote(query)
            loc_encoded = urllib.parse.quote(location)
            
            # Domain key based on country
            domain = "in.indeed.com"
            if country.lower() in ["uae", "ae", "united arab emirates"]:
                 domain = "ae.indeed.com"
                 if location.lower() == "india": # Reset default if not specific
                      loc_encoded = "Dubai"

            url = f"https://{domain}/jobs?q={query_encoded}&l={loc_encoded}&start={(page-1)*10}"
            
            logger.info(f"Scraping Indeed (Experimental): {url}")
            
            page_obj, context = await self._get_page()
            
            # Indeed specific stealth: randomized user agent and viewport handled in BaseScraper
            # But we might need more specific headers or behavior
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Check for Cloudflare/Bot block
            content = await page_obj.content()
            if "hcaptcha" in content.lower() or "cloudflare" in content.lower():
                logger.warning("Indeed bot detection triggered. Skipping.")
                return []

            # Wait for job cards (CSS varies, common ones are .job_seen_beacon)
            try:
                await page_obj.wait_for_selector(".job_seen_beacon, .result", timeout=15000)
            except:
                logger.warning("No Indeed job cards found or timed out.")
                return []

            cards = await page_obj.query_selector_all(".job_seen_beacon")
            
            for card in cards:
                try:
                    title_el = await card.query_selector("h2.jobTitle span[title], h2.jobTitle a")
                    company_el = await card.query_selector(".companyName, [data-testid='company-name']")
                    location_el = await card.query_selector(".companyLocation, [data-testid='text-location']")
                    link_el = await card.query_selector("h2.jobTitle a")
                    
                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://in.indeed.com{link}"
                        
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on Indeed: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Indeed", country))
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
