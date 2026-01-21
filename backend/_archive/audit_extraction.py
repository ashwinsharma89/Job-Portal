
import asyncio
import logging
from scrapers.naukri_scraper import NaukriScraper
from scrapers.instahyre_scraper import InstahyreScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_experience():
    scrapers = [
        ("Naukri", NaukriScraper()),
        ("Instahyre", InstahyreScraper())
    ]
    
    query = "Software Engineer"
    location = "Bangalore"
    
    for name, scraper in scrapers:
        print(f"\n--- Testing {name} ---")
        try:
            jobs = await scraper.search_jobs(query, location)
            print(f"Found {len(jobs)} jobs")
            if jobs:
                first = jobs[0]
                print(f"Sample Job: {first['title']} at {first['company']}")
                print(f"Experience: {first['experience_min']} - {first['experience_max']} Years")
                if first['experience_min'] == 0 and first['experience_max'] == 0:
                    print("⚠️ EXTRACTION FAILED: Defaults to 0-0")
                else:
                    print("✅ EXTRACTION SUCCESSFUL")
        except Exception as e:
            print(f"Error test {name}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_experience())
