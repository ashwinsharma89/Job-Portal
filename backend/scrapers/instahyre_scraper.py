import logging
import asyncio
from typing import List, Dict, Any
from .base_scraper import BaseScraper
from playwright.async_api import Page
import urllib.parse

logger = logging.getLogger(__name__)

class InstahyreScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Instahyre.
        URL pattern: https://www.instahyre.com/{query}-jobs/
        """
        # Instahyre uses simple slug-based URLs
        query_slug = query.lower().replace(" ", "-")
        url = f"https://www.instahyre.com/{query_slug}-jobs/"
        
        logger.info(f"InstahyreScraper: Navigating to {url}")
        
        page_obj, context = await self._get_page()
        jobs = []
        
        try:
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self._random_delay(3, 5)
            
            # Instahyre uses opportunity divs
            cards = await page_obj.query_selector_all("div[class*='opportunity']")
            
            logger.info(f"Found {len(cards)} job cards on Instahyre")
            
            for card in cards:
                try:
                    # Get the link first
                    link_el = await card.query_selector("a[href*='/opportunity/']")
                    if not link_el:
                        continue
                    
                    link = await link_el.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = "https://www.instahyre.com" + link
                    
                    # Get text content
                    text = await card.inner_text()
                    lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 2]
                    
                    if not lines or len(lines) < 2:
                        continue
                    
                    # Instahyre typically shows:
                    # Line 0: Company name
                    # Line 1: Job title
                    # Line 2+: Location, experience, etc.
                    company = lines[0] if len(lines) > 0 else "Unknown Company"
                    title = lines[1] if len(lines) > 1 else query
                    
                    # If first line looks like a job title, swap
                    title_keywords = ["engineer", "developer", "manager", "analyst", "designer", "lead", "architect"]
                    if any(keyword in company.lower() for keyword in title_keywords):
                        title, company = company, title
                    
                    # Look for location in remaining lines
                    loc_text = location
                    for line in lines[2:]:
                        city_keywords = ["bangalore", "mumbai", "delhi", "hyderabad", "chennai", "pune", "remote", "work from home"]
                        if any(city in line.lower() for city in city_keywords):
                            loc_text = line
                            break
                    
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc_text,
                        "apply_link": link,
                        "description": " ".join(lines[:5])
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Instahyre"))
                    
                except Exception as e:
                    logger.debug(f"Error parsing Instahyre job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"InstahyreScraper failed: {e}")
        finally:
            await self._safe_close()
            
        return jobs
