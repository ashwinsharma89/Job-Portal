import asyncio
import logging
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.getcwd())

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from backend.managers.scraper_manager import ScraperManager

async def test_manager():
    print("Initializing ScraperManager...")
    manager = ScraperManager()
    
    print("Executing search for 'Media Analytics' in 'Bangalore'...")
    # Using a short timeout for the overall script, but let scrapers run
    jobs = await manager.execute_search("Media Analytics", "Bangalore")
    
    print(f"\nTotal jobs found: {len(jobs)}")
    
    # Analyze Experience Data
    valid_exp = [j for j in jobs if j.get('experience_max', 0) > 0]
    print(f"Jobs with valid experience (>0): {len(valid_exp)}")
    
    if valid_exp:
        print("\nSample Valid Jobs:")
        for job in valid_exp[:5]:
            print(f"- {job['company']}: {job['title']} ({job['experience_min']}-{job['experience_max']} Yrs) [{job['source']}]")
    else:
        print("\n❌ No jobs with valid experience found. Audit failed.")
        print("\n--- DEBUG: Inspecting first 5 jobs from Hirist/Foundit/Iimjobs ---")
        priority_jobs = [j for j in jobs if j['source'] in ['Hirist', 'Foundit', 'iimjobs']]
        for job in priority_jobs[:5]:
            print(f"\nSource: {job['source']}")
            print(f"Title: {job['title']}")
            print(f"Exp: {job.get('experience_min')} - {job.get('experience_max')}")
            print(f"Desc Snippet: {job.get('description')[:200]}")

if __name__ == "__main__":
    asyncio.run(test_manager())
