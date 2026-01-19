import asyncio
import logging
from scrapers.foundit_scraper import FounditScraper
from scrapers.ziprecruiter_scraper import ZipRecruiterScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.apna_scraper import ApnaScraper
from scrapers.cutshort_scraper import CutshortScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.herkey_scraper import HerKeyScraper
from scrapers.freshersworld_scraper import FreshersworldScraper
from scrapers.instahyre_scraper import InstahyreScraper
from scrapers.iimjobs_scraper import IimjobsScraper
from scrapers.hirist_scraper import HiristScraper

logging.basicConfig(level=logging.INFO)

async def test_scraper(scraper_name, scraper_instance, query, location):
    print(f"\n--- Testing {scraper_name} ---")
    try:
        jobs = await scraper_instance.search_jobs(query, location)
        print(f"Found {len(jobs)} jobs")
        if jobs:
            print(f"First job: {jobs[0].get('title')} at {jobs[0].get('company')} ({jobs[0].get('location')})")
            print(f"Link: {jobs[0].get('apply_link')}")
        else:
            print("No jobs found.")
    except Exception as e:
        print(f"Error testing {scraper_name}: {e}")

async def main():
    query = "Software Engineer"
    location = "Bangalore"
    
    scrapers = [
        ("Foundit", FounditScraper()),
        ("ZipRecruiter", ZipRecruiterScraper()),
        ("Glassdoor", GlassdoorScraper()),
        ("Apna", ApnaScraper()),
        ("Cutshort", CutshortScraper()),
        ("Indeed", IndeedScraper()),
        ("HerKey", HerKeyScraper()),
        ("Freshersworld", FreshersworldScraper()),
        ("Instahyre", InstahyreScraper()),
        ("Iimjobs", IimjobsScraper()),
        ("Hirist", HiristScraper()),
    ]
    
    for name, scraper in scrapers:
        await test_scraper(name, scraper, query, location)

if __name__ == "__main__":
    asyncio.run(main())
