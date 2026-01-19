import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def deep_inspect_site(url, site_name):
    """Deep inspection of a single site to extract job card structure"""
    print(f"\n{'='*80}")
    print(f"INSPECTING: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*80}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)  # Wait for dynamic content
            
            title = await page.title()
            print(f"Page Title: {title}\n")
            
            # Try to find job cards with various selectors
            selectors_to_try = [
                "div[class*='job-card']",
                "div[class*='jobcard']",
                "div[class*='job_card']",
                "article",
                "li[class*='job']",
                ".job-listing",
                "[data-job-id]",
                "a[href*='/job']",
                "div[class*='card']",
                ".card",
                "div[class*='listing']",
            ]
            
            best_selector = None
            best_count = 0
            
            for selector in selectors_to_try:
                try:
                    elements = await page.query_selector_all(selector)
                    count = len(elements)
                    if count > best_count and count < 200:  # Not too many (avoid false positives)
                        best_count = count
                        best_selector = selector
                except:
                    pass
            
            if best_selector and best_count > 5:
                print(f"✓ Best selector: '{best_selector}' ({best_count} elements)\n")
                
                # Get first 3 job cards
                cards = await page.query_selector_all(best_selector)
                for i, card in enumerate(cards[:3]):
                    print(f"--- Job Card {i+1} ---")
                    html = await card.evaluate("el => el.outerHTML")
                    text = await card.inner_text()
                    
                    print(f"Text content:\n{text[:300]}\n")
                    print(f"HTML (first 400 chars):\n{html[:400]}\n")
                    
                    # Try to find title, company, location
                    title_selectors = ["h2", "h3", ".title", "[class*='title']", "a"]
                    for ts in title_selectors:
                        title_el = await card.query_selector(ts)
                        if title_el:
                            title_text = await title_el.inner_text()
                            print(f"  Possible title ({ts}): {title_text[:100]}")
                    
                    # Find links
                    links = await card.query_selector_all("a")
                    if links:
                        for link in links[:2]:
                            href = await link.get_attribute("href")
                            link_text = await link.inner_text()
                            print(f"  Link: {href} ({link_text[:50]})")
                    
                    print()
            else:
                print("✗ Could not find job cards with common selectors\n")
                
                # Show all links on page
                all_links = await page.query_selector_all("a")
                job_links = []
                for link in all_links[:100]:
                    href = await link.get_attribute("href")
                    if href and any(keyword in href.lower() for keyword in ['/job', '/vacancy', '/opening', '/position']):
                        job_links.append(href)
                
                if job_links:
                    print(f"Found {len(job_links)} job-related links:")
                    for jl in job_links[:5]:
                        print(f"  - {jl}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            await browser.close()

async def main():
    sites = [
        ("https://www.hirist.tech/k/artificial-intelligence-jobs?ref=homepagetag", "Hirist"),
        ("https://www.herkey.com/search?keyword=python&moduleName=jobs", "HerKey"),
        ("https://www.instahyre.com/python-jobs/", "Instahyre"),
        ("https://www.iimjobs.com/python-jobs-in-bangalore", "Iimjobs"),
        ("https://www.foundit.in/search/software-engineer-jobs-in-bangalore", "Foundit"),
    ]
    
    for url, name in sites:
        await deep_inspect_site(url, name)
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
