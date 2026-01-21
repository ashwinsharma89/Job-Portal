import asyncio
import logging
import sys
from playwright.async_api import async_playwright

# Import all scrapers
from scrapers.instahyre_scraper import InstahyreScraper
from scrapers.iimjobs_scraper import IimjobsScraper
from scrapers.linkedin_scraper import LinkedInScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScraperDebug")

async def test_scraper(scraper_name):
    print(f"🚀 Testing Scraper: {scraper_name}")
    
    scraper = None
    if scraper_name.lower() == "instahyre":
        scraper = InstahyreScraper()
    elif scraper_name.lower() == "iimjobs":
        scraper = IimjobsScraper()
    elif scraper_name.lower() == "linkedin":
        scraper = LinkedInScraper()
    else:
        print("Unknown scraper")
        return

    # Manual Browser Launch (Mimic BrowserPool)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # use False to watch
        
        # Inject browser into scraper (bypass BrowserPool for debug)
        scraper.browser = browser
        
        
        # Override _get_page to use our context
        async def mock_get_page():
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            return page, context
        
        scraper._get_page = mock_get_page
        
        # Get query from args
        query_arg = sys.argv[2] if len(sys.argv) > 2 else "Data Scientist"
        loc_arg = sys.argv[3] if len(sys.argv) > 3 else "Delhi"
        
        print(f"SEARCHING {scraper_name} for '{query_arg}' in '{loc_arg}'...")
        jobs = await scraper.search_jobs(query_arg, loc_arg, 1)
        
        print(f"📊 {scraper_name} Found {len(jobs)} jobs.")
        
        if len(jobs) == 0:
            print("❌ Zero jobs found. Dumping page content snippet...")
            pages = scraper.browser.contexts[0].pages
            if pages:
                 content = await pages[0].content()
                 print(content[:2000]) # Print first 2000 chars
            else:
                 print("No pages open to dump.")

        for j in jobs[:3]:
            print(f"   - {j['title']} @ {j['company']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 debug_scraper_tool.py <instahyre|iimjobs>")
    else:
        asyncio.run(test_scraper(sys.argv[1]))
