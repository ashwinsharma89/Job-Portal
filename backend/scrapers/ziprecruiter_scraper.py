import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse

logger = logging.getLogger(__name__)

class ZipRecruiterScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on ZipRecruiter.
        URL: https://www.ziprecruiter.com/jobs-search?search={query}&location={location}
        """
        jobs = []
        try:
            query_encoded = urllib.parse.quote(query)
            location_encoded = urllib.parse.quote(location)
            
            # ZipRecruiter uses search and location params
            # Note: start/page might vary, but standard is often &page=N
            url = f"https://www.ziprecruiter.com/jobs-search?search={query_encoded}&location={location_encoded}&page={page}"
            
            logger.info(f"Scraping ZipRecruiter: {url}")
            
            page_obj, context = await self._get_page()
            
            # ZipRecruiter has Cloudflare/Bot protection
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Brief wait for animations/content
            await asyncio.sleep(2)
            
            # Check for Cloudflare/Access Denied
            content = await page_obj.content()
            if "Access Denied" in content or "hcaptcha" in content.lower():
                logger.warning("ZipRecruiter bot detection triggered. Skipping.")
                return []

            # Wait for job cards
            # Modern ZipRecruiter uses [data-testid="job-card"]
            try:
                await page_obj.wait_for_selector('[data-testid="job-card"], .job_content', timeout=15000)
            except:
                logger.warning(f"No job cards found on ZipRecruiter for '{query}' in '{location}'")
                return []

            cards = await page_obj.query_selector_all('[data-testid="job-card"], .job_content')
            
            for card in cards:
                try:
                    # Title is usually an h2 or has a specific data-testid
                    title_el = await card.query_selector('h2, [data-testid="job-card-title"]')
                    company_el = await card.query_selector('[data-testid="job-card-company"], .company_name')
                    location_el = await card.query_selector('[data-testid="job-card-location"], .location')
                    
                    # Link is often either the card itself if it's an 'a' tag, or a link inside
                    link_el = await card.query_selector('a[href*="/jobs/"]')
                    if not link_el and card.tag_name() == 'a':
                        link_el = card

                    title = await title_el.inner_text() if title_el else "Unknown Role"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    loc = await location_el.inner_text() if location_el else location
                    link = await link_el.get_attribute("href") if link_el else ""
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.ziprecruiter.com{link}"

                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": f"View details on ZipRecruiter: {link}"
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "ZipRecruiter"))
                except Exception as e:
                    logger.debug(f"Error parsing ZipRecruiter job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"ZipRecruiter scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
