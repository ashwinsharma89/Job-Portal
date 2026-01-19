
import asyncio
import logging
import urllib.parse
from scrapers.indeed_scraper import IndeedScraper
from scrapers.naukrigulf_scraper import NaukriGulfScraper
from scrapers.bayt_scraper import BaytScraper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scrapers():
    query = "Python"
    location = "Dubai"
    country = "UAE"
    
    # Test Indeed
    print("Testing Indeed...")
    try:
        scraper = IndeedScraper()
        jobs = await scraper.search_jobs(query, location, country=country)
        print(f"Indeed found {len(jobs)} jobs")
        if len(jobs) > 0:
            print(jobs[0])
    except Exception as e:
        print(f"Indeed Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test NaukriGulf
    print("\nTesting NaukriGulf...")
    try:
        scraper = NaukriGulfScraper()
        jobs = await scraper.search_jobs(query, location, country=country)
        print(f"NaukriGulf found {len(jobs)} jobs")
        if len(jobs) > 0:
            print(jobs[0])
    except Exception as e:
        print(f"NaukriGulf Failed: {e}")
        import traceback
        traceback.print_exc()

    # Test Bayt
    print("\nTesting Bayt...")
    try:
        scraper = BaytScraper()
        jobs = await scraper.search_jobs(query, location, country=country)
        print(f"Bayt found {len(jobs)} jobs")
        if len(jobs) > 0:
            print(jobs[0])
    except Exception as e:
        print(f"Bayt Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scrapers())
