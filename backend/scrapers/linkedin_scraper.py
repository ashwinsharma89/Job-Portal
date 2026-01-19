import logging
import asyncio
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper
from datetime import datetime
import urllib.parse

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from LinkedIn India (Guest mode) using Playwright.
        """
        jobs_list = []
        page_obj = None
        try:
            page_obj, context = await self._get_page()
            
            # Format LinkedIn search URL for guest access
            # Example: https://www.linkedin.com/jobs/search/?keywords=python&location=India
            encoded_query = urllib.parse.quote(query)
            encoded_loc = urllib.parse.quote(location)
            url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}&location={encoded_loc}&f_TPR=r604800" # Past week
            
            logger.info(f"LinkedInScraper: Navigating to {url}")
            await page_obj.goto(url, wait_until="networkidle", timeout=60000)
            
            # LinkedIn often triggers a login wall if scaping too fast
            await self._random_delay(2, 4)
            
            # Scroll to load more
            for _ in range(2):
                await page_obj.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self._random_delay(1, 2)

            # Selectors for LinkedIn Guest Jobs
            # Browser inspection showed '.base-search-card'
            try:
                await page_obj.wait_for_selector(".base-search-card", timeout=15000)
            except:
                logger.warning("LinkedInScraper: Job cards selector '.base-search-card' not found.")
                # Guest view also uses .base-card
                try:
                    await page_obj.wait_for_selector(".base-card", timeout=5000)
                except:
                    return []

            job_cards = await page_obj.query_selector_all(".base-search-card")
            if not job_cards:
                job_cards = await page_obj.query_selector_all(".base-card")
            
            logger.info(f"LinkedInScraper: Found {len(job_cards)} job cards")

            for card in job_cards[:20]:
                try:
                    title_el = await card.query_selector(".base-search-card__title")
                    if not title_el: title_el = await card.query_selector("h3")
                    title = (await title_el.inner_text()).strip() if title_el else "Unknown Role"
                    
                    company_el = await card.query_selector(".base-search-card__subtitle")
                    if not company_el: company_el = await card.query_selector("h4")
                    company = (await company_el.inner_text()).strip() if company_el else "Unknown Company"
                    
                    link_el = await card.query_selector("a.base-card__full-link")
                    if not link_el: link_el = await card.query_selector("a")
                    apply_link = await link_el.get_attribute("href") if link_el else ""
                    
                    loc_el = await card.query_selector(".job-search-card__location")
                    if not loc_el: loc_el = await card.query_selector(".base-search-card__metadata")
                    location_text = (await loc_el.inner_text()).strip() if loc_el else location
                    
                    # LinkedIn guest view doesn't easily show description or exp on search page
                    # It would require clicking each job, which increases detection risk.
                    # We'll skip deep scraping for now to stay stealthy.

                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "apply_link": apply_link,
                        "description": f"View full description on LinkedIn: {apply_link}",
                        "posted_at": datetime.now()
                    }
                    
                    jobs_list.append(self.normalize_job_data(raw_job, "LinkedIn India"))
                    
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"LinkedInScraper error: {e}")
        finally:
            if page_obj:
                await page_obj.close()
        
        return jobs_list
