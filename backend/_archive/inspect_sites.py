import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def inspect_site(url, site_name):
    print(f"\n{'='*60}")
    print(f"Inspecting {site_name}: {url}")
    print(f"{'='*60}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)  # Wait for dynamic content
            
            # Get page title
            title = await page.title()
            print(f"Page Title: {title}")
            
            # Try various common selectors
            selectors_to_try = [
                "div[class*='job']",
                "div[class*='card']",
                "article",
                "li[class*='job']",
                "a[href*='/job']",
                "[data-test*='job']",
                "[data-testid*='job']",
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        print(f"✓ Found {len(elements)} elements with selector: {selector}")
                        
                        # Get first element's HTML
                        if elements:
                            first_html = await elements[0].evaluate("el => el.outerHTML")
                            print(f"  First element preview (truncated):")
                            print(f"  {first_html[:300]}...")
                except Exception as e:
                    pass
            
            # Get all links
            links = await page.query_selector_all("a")
            job_links = []
            for link in links[:50]:  # Check first 50 links
                href = await link.get_attribute("href")
                if href and ("/job" in href.lower() or "/vacancy" in href.lower() or "/opening" in href.lower()):
                    job_links.append(href)
            
            if job_links:
                print(f"\n✓ Found {len(job_links)} job-related links")
                print(f"  Sample links: {job_links[:3]}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            await browser.close()

async def main():
    sites = [
        ("https://www.foundit.in/search/software-engineer-jobs-in-bangalore", "Foundit"),
        ("https://www.instahyre.com/software-engineer-jobs-in-bangalore/", "Instahyre"),
        ("https://www.iimjobs.com/software-engineer-jobs-in-bangalore", "Iimjobs"),
    ]
    
    for url, name in sites:
        await inspect_site(url, name)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
