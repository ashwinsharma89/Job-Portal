import asyncio
import logging
from scrapers.naukri_scraper import NaukriScraper
from playwright.async_api import async_playwright

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NaukriDebug")

async def test_naukri():
    scraper = NaukriScraper()
    # Manually initialize browser since we are not using ScraperManager
    async with async_playwright() as p:
        # Use a real User-Agent to avoid immediate blocking
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        scraper.browser = browser # Hack to pass browser
        
        # Override _get_page to use our context
        async def mock_get_page():
            page = await context.new_page()
            return page, context
        scraper._get_page = mock_get_page
        
        print("🚀 Starting Naukri Scrape Test (Stealth Mode)...")
        jobs = await scraper.search_jobs("Data Scientist", "Delhi NCR", 1)
        
        print(f"📊 Found {len(jobs)} jobs.")
        
        if len(jobs) > 0:
            print(f"✅ Sample 1: {jobs[0]['title']} at {jobs[0]['company']}")
        else:
            print("❌ No jobs found. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(test_naukri())
