import asyncio
import logging
from scrapers.foundit_scraper import FounditScraper
from scrapers.instahyre_scraper import InstahyreScraper
from scrapers.iimjobs_scraper import IimjobsScraper
from scrapers.hirist_scraper import HiristScraper
from scrapers.herkey_scraper import HerKeyScraper

logging.basicConfig(level=logging.INFO)

async def test_scraper(scraper_name, scraper_instance, query, location):
    print(f"\n{'='*60}")
    print(f"Testing {scraper_name}")
    print(f"{'='*60}")
    try:
        jobs = await scraper_instance.search_jobs(query, location)
        print(f"✓ Found {len(jobs)} jobs")
        if jobs:
            print(f"\nFirst 3 jobs:")
            for i, job in enumerate(jobs[:3], 1):
                print(f"  {i}. {job.get('title')} at {job.get('company')}")
                print(f"     Location: {job.get('location')}")
                print(f"     Link: {job.get('apply_link')}")
        else:
            print("✗ No jobs found.")
    except Exception as e:
        print(f"✗ Error testing {scraper_name}: {e}")
        import traceback
        traceback.print_exc()

async def main():
    query = "Python"
    location = "Bangalore"
    
    print(f"\n{'#'*60}")
    print(f"# Testing Priority Scrapers")
    print(f"# Query: {query}, Location: {location}")
    print(f"{'#'*60}")
    
    scrapers = [
        ("Hirist", HiristScraper()),
        ("Foundit", FounditScraper()),
        ("HerKey", HerKeyScraper()),
        ("Instahyre", InstahyreScraper()),
        ("Iimjobs", IimjobsScraper()),
    ]
    
    for name, scraper in scrapers:
        await test_scraper(name, scraper, query, location)
        await asyncio.sleep(2)  # Brief pause between scrapers

if __name__ == "__main__":
    asyncio.run(main())
