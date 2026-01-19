import logging
import asyncio
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper
from datetime import datetime

logger = logging.getLogger(__name__)

class NaukriScraper(BaseScraper):
    async def search_jobs(self, query: str, location: str = "India", page: int = 1) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Naukri.com using Playwright.
        """
        jobs_list = []
        page_obj = None
        try:
            # context = await self.browser.new_context(user_agent=mobile_ua)
            # Since we use BrowserPool, we get a page and context directly.
            # However, Naukri wants a specific mobile UA. 
            # BrowserPool currently provides a random desktop UA.
            # For now, let's use the standard pool page to avoid complexity.
            
            page_obj, context = await self._get_page()
            
            # Form Naukri search URL directly but with mobile-optimized parameters if possible
            search_query = query.replace(" ", "-")
            search_loc = location.replace(" ", "-")
            url = f"https://www.naukri.com/{search_query}-jobs-in-{search_loc}?k={query}&l={location}"
            
            logger.info(f"NaukriScraper: Navigating to mobile URL {url}")
            await page_obj.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Allow some time for Akamai/JS
            await asyncio.sleep(5)
            
            # Scroll down to trigger lazy loading if any
            await page_obj.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await self._random_delay(1, 2)

            # Wait for job cards to appear
            try:
                # Browser inspection showed '.cust-job-tuple'
                await page_obj.wait_for_selector(".cust-job-tuple", timeout=15000)
            except:
                title = await page_obj.title()
                logger.warning(f"NaukriScraper: Job cards selector '.cust-job-tuple' not found. Page title: {title}")
                # Save a snippet of content for debugging
                content = await page_obj.content()
                logger.warning(f"NaukriScraper: Page content snippet: {content[:500]}")
                
                try:
                    await page_obj.wait_for_selector("div[class*='tuple']", timeout=5000)
                except:
                    logger.warning("NaukriScraper: Fallback tuple selector also not found.")
                    return []

            job_cards = await page_obj.query_selector_all(".cust-job-tuple")
            if not job_cards:
                job_cards = await page_obj.query_selector_all("div[class*='tuple']")
            
            # If still not found, try any div with 'job' or 'card' in class
            if not job_cards:
                 job_cards = await page_obj.query_selector_all("div[class*='job']")
            
            logger.info(f"NaukriScraper: Found {len(job_cards)} job cards")

            for card in job_cards[:20]: # Fetch more if possible
                try:
                    title_el = await card.query_selector("a.title")
                    title = (await title_el.inner_text()).strip() if title_el else "Unknown Role"
                    
                    company_el = await card.query_selector(".comp-name")
                    company = (await company_el.inner_text()).strip() if company_el else "Unknown Company"
                    
                    apply_link = await title_el.get_attribute("href") if title_el else ""
                    
                    # Naukri structure often uses spans within a div for meta info
                    exp_el = await card.query_selector(".expwdth")
                    exp_text = (await exp_el.inner_text()).strip() if exp_el else "0-0 Yrs"
                    
                    # Simple parsing of "0-5 Yrs"
                    exp_min = 0
                    exp_max = 0
                    if "-" in exp_text:
                        parts = exp_text.replace("Yrs", "").replace("yr", "").strip().split("-")
                        try:
                            exp_min = int(''.join(filter(str.isdigit, parts[0])))
                            exp_max = int(''.join(filter(str.isdigit, parts[1])))
                        except:
                            pass
                    
                    loc_el = await card.query_selector(".loc-wrap")
                    location_text = (await loc_el.inner_text()).strip() if loc_el else location
                    
                    desc_el = await card.query_selector(".job-description")
                    description = (await desc_el.inner_text()).strip() if desc_el else ""
                    
                    # Skills often in '.tag-container' or specific classes
                    skills_els = await card.query_selector_all(".dot-gt-tag")
                    if not skills_els:
                        skills_els = await card.query_selector_all("li.dot-gt-tag")
                    skills = [(await s.inner_text()).strip() for s in skills_els]

                    raw_job = {
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "experience_min": exp_min,
                        "experience_max": exp_max,
                        "apply_link": apply_link,
                        "description": description,
                        "skills": skills,
                        "posted_at": datetime.now() # Naukri dates are often relative like "3 days ago"
                    }
                    
                    jobs_list.append(self.normalize_job_data(raw_job, "Naukri.com"))
                    
                except Exception as e:
                    logger.error(f"Error parsing Naukri job card: {e}")
                    continue

        except Exception as e:
            logger.error(f"NaukriScraper error: {e}")
        finally:
            if page_obj:
                await page_obj.close()
            # We don't close browser here to reuse it for other sources if needed, 
            # though usually we call _safe_close at the end of the batch.
        
        return jobs_list
