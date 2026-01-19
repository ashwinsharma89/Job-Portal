import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse
import re

logger = logging.getLogger(__name__)

class GlassdoorScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on Glassdoor.co.in.
        URL Pattern: https://www.glassdoor.co.in/Job/india-{query}-jobs-SRCH_IL.0,5_IN115_KO6,{query_len}.htm
        Note: Glassdoor has extremely strong bot detection.
        """
        jobs = []
        try:
            # Glassdoor uses a complex URL structure. 
            # We'll try a search-based URL if possible, or construct the slug if we can.
            query_slug = query.lower().replace(" ", "-")
            # For India, SRCH_IL.0,5_IN115 is common. KO6,X is keyword offset.
            # keyword offset usually starts after 'india-' (6 chars)
            keyword_len = len(query_slug)
            
            # This is a best-guess URL structure for Glassdoor India
            url = f"https://www.glassdoor.co.in/Job/india-{query_slug}-jobs-SRCH_IL.0,5_IN115_KO6,{6+keyword_len}.htm"
            
            logger.info(f"Scraping Glassdoor (Experimental): {url}")
            
            page_obj, context = await self._get_page()
            
            # Glassdoor requires strong stealth and potentially many retries
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            await asyncio.sleep(3) # Extra wait for Cloudflare
            
            content = await page_obj.content()
            if "hcaptcha" in content.lower() or "cloudflare" in content.lower() or "Access Denied" in content:
                logger.warning("Glassdoor bot detection triggered. Skipping.")
                return []

            # Wait for job cards (data-test="jobListing" is standard)
            try:
                await page_obj.wait_for_selector('li[data-test="jobListing"]', timeout=15000)
            except:
                logger.warning(f"No job cards found on Glassdoor for '{query}' in India")
                return []

            cards = await page_obj.query_selector_all('li[data-test="jobListing"]')
            
            for card in cards:
                try:
                    title_el = await card.query_selector('[data-test="job-title"]')
                    company_el = await card.query_selector('[data-test="employer-name"]')
                    location_el = await card.query_selector('[data-test="location"]')
                    link_el = await card.query_selector('[data-test="job-link"]')

                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    # Company name on Glassdoor often contains rating (e.g. "Google 4.5")
                    company = re.sub(r'\s\d\.\d$', '', company.strip())
                    
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.glassdoor.co.in{link}"

                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on Glassdoor: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Glassdoor"))
                except Exception as e:
                    logger.debug(f"Error parsing Glassdoor job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Glassdoor scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
