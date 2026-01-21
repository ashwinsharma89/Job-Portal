import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def inspect_priority_sites():
    """Inspect the 5 priority sites to understand their structure"""
    
    sites = [
        {
            "name": "Hirist",
            "urls": [
                "https://www.hirist.tech/jobs/search?q=Software%20Engineer&location=Bangalore",
                "https://www.hirist.tech/k/software-engineer-jobs-in-bangalore-1.html",
                "https://www.hirist.tech/jobs?search=Software%20Engineer"
            ]
        },
        {
            "name": "Foundit",
            "urls": [
                "https://www.foundit.in/search/software-engineer-jobs-in-bangalore"
            ]
        },
        {
            "name": "HerKey",
            "urls": [
                "https://www.herkey.com/jobs/search?location=Bangalore&keyword=Software%20Engineer",
                "https://www.herkey.com/jobs?search=Software%20Engineer"
            ]
        },
        {
            "name": "Instahyre",
            "urls": [
                "https://www.instahyre.com/search-jobs?q=Software%20Engineer&location=Bangalore",
                "https://www.instahyre.com/software-engineer-jobs-in-bangalore/",
                "https://www.instahyre.com/jobs"
            ]
        },
        {
            "name": "Iimjobs",
            "urls": [
                "https://www.iimjobs.com/j/software-engineer-jobs.html",
                "https://www.iimjobs.com/jobs/software-engineer",
                "https://www.iimjobs.com/software-engineer-jobs-in-bangalore"
            ]
        }
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        for site in sites:
            print(f"\n{'='*80}")
            print(f"TESTING: {site['name']}")
            print(f"{'='*80}")
            
            for url in site['urls']:
                page = await browser.new_page()
                try:
                    print(f"\n  URL: {url}")
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(3)
                    
                    title = await page.title()
                    final_url = page.url
                    
                    print(f"  ✓ Title: {title}")
                    if final_url != url:
                        print(f"  ⚠ Redirected to: {final_url}")
                    
                    # Check for job cards
                    selectors = [
                        ("div[class*='job-card']", "Job card divs"),
                        ("div[class*='jobcard']", "Jobcard divs"),
                        ("article", "Article elements"),
                        ("li[class*='job']", "Job list items"),
                        (".job-listing", "Job listing class"),
                        ("[data-job-id]", "Data job ID"),
                        ("a[href*='/job']", "Job links"),
                    ]
                    
                    found_any = False
                    for selector, desc in selectors:
                        elements = await page.query_selector_all(selector)
                        if len(elements) > 5:  # More than 5 suggests actual job listings
                            print(f"  ✓ {desc}: {len(elements)} elements")
                            found_any = True
                            
                            # Show first element structure
                            if elements:
                                first = await elements[0].evaluate("el => el.outerHTML")
                                print(f"    Sample HTML: {first[:200]}...")
                    
                    if not found_any:
                        print(f"  ✗ No job listings found with common selectors")
                        # Get page content to see what's there
                        content = await page.content()
                        if "login" in content.lower() or "sign in" in content.lower():
                            print(f"  ⚠ Page may require login")
                        if "captcha" in content.lower() or "robot" in content.lower():
                            print(f"  ⚠ Bot detection detected")
                    
                    print(f"  {'─'*76}")
                    
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                finally:
                    await page.close()
                    await asyncio.sleep(1)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_priority_sites())
