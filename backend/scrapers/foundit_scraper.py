import asyncio
import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper
import urllib.parse
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class FounditScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for jobs on foundit.in.
        URL: https://www.foundit.in/search/{query}-jobs-in-{location}
        """
        jobs = []
        try:
            # Foundit uses slug-based URLs for better SEO
            query_slug = query.lower().replace(" ", "-")
            location_slug = location.lower().replace(" ", "-")
            
            # Base search URL
            url = f"https://www.foundit.in/search/{query_slug}-jobs-in-{location_slug}"
            
            if page > 1:
                url += f"?start={(page-1)*15}"  # Foundit usually shows 15-20 per page

            logger.info(f"Scraping Foundit: {url}")
            
            page_obj, context = await self._get_page()
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._random_delay(3, 5)
            
            # Wait for job cards - Foundit uses card-based layout
            try:
                await page_obj.wait_for_selector('div[class*="card"]', timeout=10000)
            except:
                logger.warning(f"FounditScraper: Job cards not found. Saving debug snapshot.")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                await page_obj.screenshot(path=f"debug_dumps/foundit_fail_{timestamp}.png")
                content = await page_obj.content()
                with open(f"debug_dumps/foundit_fail_{timestamp}.html", "w") as f:
                    f.write(content)
                logger.info(f"FounditScraper: Snapshot saved to debug_dumps/foundit_fail_{timestamp}.png")
                return []

            # Get job card containers
            cards = await page_obj.query_selector_all('div[class*="job-card"], div[class*="jobcard"], div.shadow-job-card')
            
            logger.info(f"Found {len(cards)} job cards on Foundit")
            
            for card in cards:
                try:
                    # Get title link
                    title_el = await card.query_selector("h2 a, h3 a, a[aria-label]")
                    if not title_el:
                        continue
                    
                    title = await title_el.inner_text()
                    link = await title_el.get_attribute("href")
                    
                    if link and not link.startswith("http"):
                        link = f"https://www.foundit.in{link}"
                    
                    # Get company
                    company_el = await card.query_selector("a[class*='company'], div[class*='company']")
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    
                    # Get location, experience, and ctc from labels
                    loc = location
                    exp_min = 0
                    exp_max = 0
                    ctc_str = ""
                    
                    labels = await card.query_selector_all("label, span[class*='location'], div[class*='location'], div[class*='details']")
                    for label in labels:
                        text = await label.inner_text()
                        text_lower = text.lower()
                        
                        # Extract Experience
                        if "year" in text_lower or "yrs" in text_lower:
                            # Parse "5-10 years" or "5-10 yrs"
                            # Regex basic
                            import re
                            # Check for range "5-10"
                            matches = re.findall(r'(\d+)\s*-\s*(\d+)', text)
                            if matches:
                                exp_min = int(matches[0][0])
                                exp_max = int(matches[0][1])
                            else:
                                # Check for "5+ years" or just "2 Years"
                                match = re.search(r'(\d+)\+', text)
                                if match:
                                    exp_min = int(match.group(1))
                                    exp_max = 99
                                else:
                                    # "2 Years" -> min 2, max 2
                                    match_single = re.search(r'(\d+)', text)
                                    if match_single:
                                        val = int(match_single.group(1))
                                        exp_min = val
                                        exp_max = val

                        
                        # Extract CTC
                        elif "lpa" in text_lower:
                            ctc_str = text.strip()

                        # Extract Location (if not experience/ctc)
                        elif "year" not in text_lower and "lpa" not in text_lower and any(char.isalpha() for char in text):
                            if any(city in text for city in ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune", "India"]):
                                loc = text.strip()

                    # Construct description from all text in card if possible
                    full_text = await card.inner_text()
                    
                    raw_job = {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "apply_link": link,
                        "description": full_text.strip() if full_text else f"View details on Foundit: {link}",
                        "experience_min": exp_min,
                        "experience_max": exp_max,
                        "ctc": ctc_str # Base scraper logic might need `ctc_min` but `ctc` string is often passed
                    }
                    
                    jobs.append(self.normalize_job_data(raw_job, "Foundit"))
                except Exception as e:
                    logger.debug(f"Error parsing Foundit job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Foundit scraping error: {e}")
        finally:
            await self._safe_close()
            
        return jobs
