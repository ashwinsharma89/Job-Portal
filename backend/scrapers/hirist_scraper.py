import logging
import asyncio
from typing import List, Dict, Any
from .base_scraper import BaseScraper
from playwright.async_api import Page
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

class HiristScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Hirist.tech.
        URL pattern: https://www.hirist.tech/k/{query}-jobs
        """
        # Hirist uses simple slug-based URLs
        query_slug = query.lower().replace(" ", "-")
        url = f"https://www.hirist.tech/k/{query_slug}-jobs"
        
        logger.info(f"HiristScraper: Navigating to {url}")
        
        # Debug trace
        try:
            with open("debug_dumps/hirist_start.txt", "a") as f:
                f.write(f"Started Hirist scrape for {url} at {datetime.now()}\n")
        except: pass
        
        page_obj, context = await self._get_page()
        jobs = []
        
        try:
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=60000)
            await self._random_delay(3, 5)
            
            # Hirist uses MUI card components
            try:
                await page_obj.wait_for_selector("div.joblist-card-v2, div.MuiCard-root", timeout=15000)
            except:
                logger.warning("HiristScraper: Job cards not found immediately. Saving debug snapshot.")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page_obj.screenshot(path=f"debug_dumps/hirist_fail_{timestamp}.png")
                content = await page_obj.content()
                with open(f"debug_dumps/hirist_fail_{timestamp}.html", "w") as f:
                    f.write(content)
                logger.info(f"HiristScraper: Snapshot saved to debug_dumps/hirist_fail_{timestamp}.png")

            cards = await page_obj.query_selector_all("div.joblist-card-v2, div.MuiCard-root")
            
            logger.info(f"Found {len(cards)} job cards on Hirist")
            
            for card in cards:
                try:
                    # Get the main link
                    link_el = await card.query_selector("a")
                    if not link_el:
                        continue
                    
                    link = await link_el.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = "https://www.hirist.tech" + link
                    
                    # Get full text content
                    text = await card.inner_text()
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    
                    if not lines:
                        continue
                    
                    # First line is usually "Company - Title" or just "Title"
                    title_line = lines[0]
                    company = "Various"
                    title = title_line
                    
                    if " - " in title_line:
                        parts = title_line.split(" - ", 1)
                        company = parts[0].strip()
                        title = parts[1].strip() if len(parts) > 1 else title_line
                    
                    # Look for experience (e.g., "3 - 6 yrs")
                    experience = ""
                    exp_min = 0
                    exp_max = 0
                    
                    for line in lines:
                        if "yrs" in line.lower() or "years" in line.lower():
                            experience = line
                            # Parse "3 - 6 yrs"
                            import re
                            matches = re.findall(r'(\d+)\s*-\s*(\d+)', line)
                            if matches:
                                exp_min = int(matches[0][0])
                                exp_max = int(matches[0][1])
                            else:
                                # Try "5+ years"
                                match = re.search(r'(\d+)\+', line)
                                if match:
                                    exp_min = int(match.group(1))
                                    exp_max = 99
                            break
                    
                    # Look for location
                    loc_text = location
                    location_keywords = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "Gurgaon", "Noida", "Multiple Locations"]
                    for line in lines:
                        if any(city.lower() in line.lower() for city in location_keywords):
                            loc_text = line
                            break
                    
                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": loc_text,
                        "apply_link": link,
                        "description": f"{experience}. {text[:400]}" if experience else text[:500],
                        "experience_min": exp_min,
                        "experience_max": exp_max
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Hirist"))
                    
                except Exception as e:
                    logger.debug(f"Error parsing Hirist job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"HiristScraper failed: {e}")
        finally:
            await self._safe_close()
            
        return jobs
