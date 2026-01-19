import logging
import asyncio
from typing import List, Dict, Any
from .base_scraper import BaseScraper
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class IimjobsScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from iimjobs.com.
        URL pattern: https://www.iimjobs.com/{query}-jobs-in-{location}
        """
        query_slug = query.lower().replace(" ", "-")
        location_slug = location.lower().replace(" ", "-")
        url = f"https://www.iimjobs.com/{query_slug}-jobs-in-{location_slug}"
        
        logger.info(f"IimjobsScraper: Navigating to {url}")
        
        page_obj, context = await self._get_page()
        jobs = []
        
        try:
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self._random_delay(3, 5)
            
            # iimjobs uses anchor tags with /j/ in href, but sometimes div containers
            # Try getting all large anchor tags or cards
            cards = await page_obj.query_selector_all("a[href*='/j/'], div.job-label")
            
            logger.info(f"Found {len(cards)} job cards on Iimjobs")
            
            for card in cards:
                try:
                    # Get link
                    link = await card.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = "https://www.iimjobs.com" + link
                    
                    # Get text content
                    text = await card.inner_text()
                    lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 2]
                    
                    if not lines or len(lines) < 1:
                        continue
                    
                    # First line is usually the job title
                    title = lines[0]
                    
                    # Look for company and location in subsequent lines
                    company = "Various"
                    loc_text = location
                    
                    for line in lines[1:]:
                        # Check if line contains location keywords
                        if any(city in line for city in ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Gurgaon", "Noida"]):
                            loc_text = line
                        # Check for experience line
                        elif "yrs" in line.lower() or "years" in line.lower():
                            exp_text = line
                            # Parse "3-6 yrs"
                            import re
                            matches = re.findall(r'(\d+)\s*-\s*(\d+)', line)
                            if matches:
                                exp_min = int(matches[0][0])
                                exp_max = int(matches[0][1])
                            else:
                                match = re.search(r'(\d+)\+', line)
                                if match:
                                    exp_min = int(match.group(1))
                                    exp_max = 99
                        # Other lines might be company if not posted date
                        elif "posted" not in line.lower() and len(line) > 3:
                            if company == "Various":
                                company = line
                    
                    # Skip if title looks like navigation or UI element
                    skip_keywords = ["view", "login", "signup", "apply", "save", "share"]
                    if any(keyword == title.lower() for keyword in skip_keywords):
                        continue
                    
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc_text,
                        "apply_link": link,
                        "description": " ".join(lines[:4]),
                        "experience_min": locals().get('exp_min', 0),
                        "experience_max": locals().get('exp_max', 0)
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "iimjobs"))
                    
                except Exception as e:
                    logger.debug(f"Error parsing iimjobs job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"IimjobsScraper failed: {e}")
        finally:
            await self._safe_close()
            
        return jobs
